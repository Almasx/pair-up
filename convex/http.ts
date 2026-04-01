import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { internal } from "./_generated/api";

const http = httpRouter();

// Cal.com fires this webhook when a booking is created/confirmed.
// It looks up both users by email and stores the session in the DB.
http.route({
  path: "/webhooks/cal",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json();

    if (body.triggerEvent !== "BOOKING_CREATED") {
      return new Response(null, { status: 200 });
    }

    const { payload } = body;
    const organizerEmail: string = payload.organizer?.email;
    const attendeeEmail: string = payload.attendees?.[0]?.email;
    const startTime: string = payload.startTime;
    const meetingUrl: string | undefined =
      payload.videoCallData?.url ?? payload.meetingUrl;
    const calBookingUid: string = payload.uid;
    const interviewTypeName: string | undefined =
      payload.metadata?.interviewType;

    if (!organizerEmail || !attendeeEmail || !startTime) {
      return new Response("Missing required booking fields", { status: 400 });
    }

    await ctx.runMutation(internal.sessions.createFromWebhook, {
      organizerEmail,
      attendeeEmail,
      scheduledAt: new Date(startTime).getTime(),
      meetingLink: meetingUrl,
      calBookingUid,
      interviewTypeName,
    });

    return new Response(null, { status: 200 });
  }),
});

export default http;
