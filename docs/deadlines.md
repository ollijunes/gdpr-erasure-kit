# Deadlines and reminders

[Suomeksi](maaraajat.md)

A controller has one month to answer an erasure or access request. This page
explains how the kit counts that month, when it reminds you, and what to do
when the answer does not come.

The rules come from GDPR Article 12(3) and the European Data Protection
Board's [Guidelines 01/2022 on the right of access](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-012022-data-subject-rights-right-access_en),
version 2.1, paragraphs 159 to 162. The guidelines apply the general EU rules
on time limits (Regulation 1182/71). They were written for access requests;
Article 12(3) sets the same time limit for erasure.

## How the month is counted

| Rule | Example |
| --- | --- |
| The month starts on the day the controller receives your request. | Received 5 March |
| The deadline is the same date in the following month. | Answer due by 5 April |
| If the next month has no such date, the deadline is its last day. | 31 August → 30 September, 31 January → 28 February (29 in a leap year) |
| If the deadline falls on a Saturday or Sunday, it moves to the next Monday. | Saturday 5 April 2025 → Monday 7 April 2025 |
| A public holiday also moves the deadline to the next working day. | The kit does not know holidays; check your country's calendar |

"One month" is often described as 30 days. It is not always 30 days. February
is shorter, and some months have 31. The kit counts calendar months, the way
the EDPB guidelines do.

The kit counts from the date you send the request. Email and web forms usually
arrive the same day. If you send a letter, the month starts when it arrives,
so the real deadline is a few days later than the one in your tracker.

## Extensions

A controller may extend the deadline by two further months when the request
is complex or it has received many requests. It must tell you within the first
month and explain why. The EDPB says extensions are an exception, not routine.

When a controller extends, set the row's status to `extended`. The kit then
counts three months from receipt, with the same end-of-month and weekend
rules.

## When the controller asks who you are

A controller may ask for information it needs to confirm your identity
(Article 12(6)). The request must be proportionate. It should not ask for more
than it needs, and a copy of an ID card is rarely necessary when you write
from the email address that is registered to your account.

The EDPB says the time limit is suspended until the controller has the
information it asked for, provided it asked without undue delay. Set the status
to `identity_requested`. When you have answered, write that date in
`identity_sent_on`.

The kit then counts a new month from `identity_sent_on`. This is the latest
deadline the controller could argue for. The actual suspension may end earlier,
because the days before the controller's question already count. Using the
later date means the kit never asks you to chase a controller too early.

## Reminders

For each request the kit computes three dates from the deadline:

| Date | When | What to do |
| --- | --- | --- |
| `reminder_on` | 5 days before the deadline | Check whether you have an answer or at least an acknowledgement. |
| `follow_up_on` | The day after the deadline | Send a short follow-up that refers to your original request and its date. |
| `escalate_on` | 14 days after the deadline | Consider a complaint to a supervisory authority. |

`gdpr-kit due --tracker tracker.csv` lists the rows that need one of these
actions today. Rows with status `completed`, `refused` or `escalated` are
closed and no longer listed. Run it weekly, or add it to your calendar.

The 5-day and 14-day offsets are the kit's own defaults, not legal limits.
You may complain to a supervisory authority at any time.

## When the answer does not come

1. Follow up once in writing. Quote your original request, the date you sent
   it, and the deadline that has passed.
2. Keep copies of everything: the request, the controller's replies, and the
   tracker row.
3. Complain to a supervisory authority under Article 77. You can choose the
   authority in the country where you live, work, or where the infringement
   happened. The EDPB keeps a [list of national authorities](https://www.edpb.europa.eu/about-edpb/about-edpb/members_en).
   In Finland it is the [Data Protection Ombudsman](https://tietosuoja.fi/en/home).

A refusal is also an answer. The controller must tell you why and that you
can complain or go to court (Article 12(4)). Record the reason in `outcome`
and set the status to `refused`.

## Using a spreadsheet instead

The same rules work as spreadsheet formulas. See [Google Sheets](google-sheets.md).
