# Channels: connect many, schedule everything in one click

PeakCut can post to as many channels as you like. Each channel has its own upload times (for example 6 videos a
day, at 8:00, 9:00, 10:00, 11:00, 12:00 and 13:00). Channels can be sorted into groups. One click puts every
ready clip on its channels' upload times.

This guide covers YouTube, which most people use. Instagram and TikTok work the same way once they are connected
(see [DEPLOY.md](DEPLOY.md#connecting-youtube-instagram-and-tiktok) for their one-time setup).

## How it fits together

- **Creators** are the people you clip. Each creator has a workspace in the sidebar: their videos, live recordings
  and clips.
- **Channels** are where clips are posted: your YouTube channels, Instagram accounts and TikTok accounts.
- Each channel takes clips from one or more creators. Several channels can share a creator, and one channel can
  take clips from several creators.
- On the **Channels** page you see every channel with its upload times, what is waiting and what goes out next.

## Part 1: register PeakCut with Google (once per PeakCut install)

Google needs to know about your copy of PeakCut before any channel can connect. It takes about ten minutes, and
you only do it once, however many channels you add later.

1. Open [Google Cloud Console](https://console.cloud.google.com/) and sign in with any Google account.
2. Create a project (top bar, **Select a project**, **New project**). Name it something like "PeakCut".
3. Go to **APIs & Services**, **Library**, search for **YouTube Data API v3**, and press **Enable**.
4. Go to **APIs & Services**, **OAuth consent screen** (on newer screens: **Google Auth Platform**, **Branding**
   and **Audience**):
   - Choose **External**, give the app a name and your email address, and save.
   - Under **Audience**, press **Publish app** so the status says **In production**. This matters: while the
     status says **Testing**, Google signs every channel out after 7 days, and only email addresses you list as
     test users can connect.
5. Go to **APIs & Services**, **Credentials**, **Create credentials**, **OAuth client ID**:
   - Application type: **Web application**.
   - Under **Authorised redirect URIs**, add PeakCut's address. Copy it from PeakCut: **Settings**,
     **Connected apps**, **YouTube**, **Set up**. On your own computer it looks like
     `http://127.0.0.1:8765/oauth/youtube/callback`. On a server it is `https://your-domain/oauth/youtube/callback`.
   - Press **Create**. Google shows a **Client ID** and a **Client secret**.
6. Back in PeakCut (**Settings**, **Connected apps**, **YouTube**, **Set up**), paste the Client ID and the
   Client secret, and press **Save**. The YouTube card now shows a **Connect** button.

When people connect, Google shows a "Google hasn't verified this app" warning until Google verifies your app. Press
**Advanced**, then **Go to PeakCut**. This is expected for your own copy.

## Part 2: connect each channel

1. In PeakCut, open **Settings**, **Connected apps**, and press **Connect** on YouTube.
2. Sign in to Google, choose the channel, and allow PeakCut to upload videos. You come back to PeakCut with the
   channel connected.
3. For the next channel, press **Add another** and do the same. Google always shows its account list, so you can
   pick a different account each time.
   - **A channel on a Brand Account** (several channels under one Google login) shows up in Google's list after
     you pick the Google account. Choose the channel there.
   - **A channel on a different Google account**: choose **Use another account** in Google's list.
4. Repeat for every channel. They all appear on the **Channels** page.

PeakCut never sees your Google password. To remove a channel, press **Disconnect** next to it in Connected apps.
Its upload times and group are remembered, so they come back if you connect it again.

## Part 3: set each channel up

On the **Channels** page, press a channel's **Times and creators** button:

- **Upload at set times each day**: turn it on and set the times. **Quick fill** does it in one go: "6 videos a
  day, first at 08:00, then every 1 hour" gives 08:00, 09:00, 10:00, 11:00, 12:00 and 13:00. You can also add or
  remove single times. A channel posts at most once per time, so 6 times means 6 videos a day.
- **How YouTube clips go out**:
  - **YouTube publishes them** (recommended). PeakCut uploads each clip up to a day before its time as a
    scheduled video, and YouTube makes it public at that time. Your computer does not have to be on at 8:00 sharp;
    it only has to be on some time the day before.
  - **PeakCut posts at the time**. The clip is uploaded at its time, so this computer must be on and PeakCut
    running.
- **Group**: put the channel in a group (make groups with **New group** at the top of the page).
- **Creators whose clips go to this channel**: tick the creators this channel takes clips from.

Instagram and TikTok channels use the same times, but PeakCut always posts those at the time itself.

To give a whole group the same times, press **Same times for all** next to the group's name.

Channels without times of their own use the **Default upload times** at the bottom of the page. With those off,
they post after each creator's gap (Setup, Posting, "Minutes between posts").

## Part 4: one click

- **Upload & schedule all** (top of the Channels page, and on Home): every finished clip that hasn't gone to a
  channel yet takes that channel's next free time, best clip first.
- **Upload & schedule group**: the same, for one group's channels.
- **Upload & schedule** on a channel: the same, for one channel.
- **Schedule all clips** on a creator's page: that creator's clips, on the channels the creator posts to.

You always see the plan first: how many clips go to each channel, and from when to when. You can also choose to
skip clips scoring below a number you pick. Nothing happens until you press **Upload & schedule**. A clip never goes
to the same channel twice, so pressing the button again only adds new clips.

Every scheduled clip is listed on Home, under **Post queue**. Clips still waiting can be cancelled there. A clip
already uploaded to YouTube as a scheduled video (shown as "On YouTube") is changed or deleted in YouTube Studio.
**Pause all posting** on Home stops all new uploads until you resume.

## YouTube's limits

- **Uploads per day.** Each Google Cloud project can upload **100 videos a day** by default, shared by every channel
  connected through it. For example, 16 channels at 6 videos a day is 96. Check yours in Google Cloud under **APIs &
  Services**, **YouTube Data API v3**, **Quotas**. When the allowance runs out, PeakCut does not count it as a failure:
  the clip waits until the allowance resets (midnight Pacific time) and goes then by itself. To upload more, ask
  Google for a higher allowance with the
  [YouTube API audit and quota extension form](https://support.google.com/youtube/contact/yt_api_form).
- **Use one Google project for all your channels.** YouTube's developer policies forbid making several Google Cloud
  projects for the same app to get more quota ("sharding"). Doing that can get every project suspended, which signs
  out all your channels at once. The quota form is the allowed way to get more.
- **Private until audited.** Google may keep videos uploaded through an unaudited project private (Google's own
  pages describe this). If your clips stay private, the same form asks Google to audit your project.
- **Each channel's own limit.** YouTube also limits how many videos one channel uploads a day. PeakCut handles that the
  same way: the clip waits and tries again after the reset.
- **A clip that misses its time** (because it waited for the reset) is not posted off schedule: it takes the
  channel's next free upload time instead.

## When something goes wrong

- **"This sign-in has expired" or posts fail with an authorisation error after a week**: the Google app is still in
  Testing. Publish it (Part 1, step 4), then press **Add another** and connect the channel again.
- **"Google did not return a long-lived sign-in"**: remove PeakCut's access at
  [myaccount.google.com/permissions](https://myaccount.google.com/permissions), then connect again.
- **"That Google account has no YouTube channel"**: create a channel on YouTube first, or pick the Brand Account
  that owns it.
- **Redirect URI mismatch**: the address in Google Cloud must match the one PeakCut shows exactly, including
  `http`/`https` and the port.
- **A clip failed**: it is listed under **Failed uploads** on Home with the reason. **Upload now** tries it again.
