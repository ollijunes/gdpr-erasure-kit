# Tracking requests in Google Sheets

You can track requests in a spreadsheet without the command line. The date
formulas also work in LibreOffice Calc and Excel; the highlighting rules are
written for Google Sheets.

## Set up the sheet

1. Download [tracker/tracker-template.csv](../tracker/tracker-template.csv).
2. In Google Sheets, choose File → Import → Upload, and pick the file.
   Choose "Replace spreadsheet". Do not let Sheets convert text to numbers or
   dates.
3. Select columns F to M and set Format → Number → Custom date and time to
   `yyyy-mm-dd`. The command line reads dates only in this form, so a CSV
   export of the sheet stays readable by `gdpr-kit due`.

The columns are:

| Column | Name | You fill in |
| --- | --- | --- |
| A | `service` | The service name |
| B | `contact` | Privacy email address or form URL |
| C | `request_type` | `erasure` or `access` |
| D | `language` | `en` or `fi` |
| E | `status` | See [statuses](#statuses) |
| F | `sent_on` | The day you sent the request |
| G | `deadline` | Formula |
| H | `reminder_on` | Formula |
| I | `follow_up_on` | Formula |
| J | `escalate_on` | Formula |
| K | `identity_sent_on` | The day you answered an identity question, if any |
| L | `extended_deadline` | Formula |
| M | `replied_on` | The day the controller answered |
| N | `outcome` | What happened, in your own words |
| O | `notes` | Anything else |

## Formulas

Put these in row 2 and fill them down. They follow the rules in
[Deadlines and reminders](deadlines.md): one calendar month from the start date,
end of month when the date does not exist, and a weekend moves the deadline to
Monday.

`G2`, deadline:

```text
=IF(OR(F2="", AND(E2="identity_requested", K2="")), "", WORKDAY(EDATE(IF(K2="", F2, K2), 1) - 1, 1))
```

`L2`, extended deadline (three months from the start date):

```text
=IF(OR(F2="", AND(E2="identity_requested", K2="")), "", WORKDAY(EDATE(IF(K2="", F2, K2), 3) - 1, 1))
```

`H2`, reminder five days before the deadline in force:

```text
=IF(G2="", "", IF(E2="extended", L2, G2) - 5)
```

`I2`, follow-up the day after:

```text
=IF(G2="", "", IF(E2="extended", L2, G2) + 1)
```

`J2`, escalation 14 days after:

```text
=IF(G2="", "", IF(E2="extended", L2, G2) + 14)
```

While the controller waits for your identity reply (`identity_requested`
with an empty `identity_sent_on`), the dates stay blank, because the clock is
suspended. They come back when you fill in `identity_sent_on`.

`EDATE` adds calendar months and stops at the end of a shorter month.
`WORKDAY(date - 1, 1)` returns the same date on a weekday and the next Monday
on a weekend. To skip public holidays too, list them in a separate sheet and
add the range as a third argument: `WORKDAY(... , 1, Holidays!A:A)`.

## Highlight what needs action

Select A2:O and add three rules in Format → Conditional formatting →
Custom formula:

| Rule | Custom formula | Suggested colour |
| --- | --- | --- |
| Reminder due | `=AND($H2<>"", TODAY()>=$H2, TODAY()<$I2, $E2<>"completed", $E2<>"refused", $E2<>"escalated")` | Light yellow |
| Deadline passed | `=AND($I2<>"", TODAY()>=$I2, TODAY()<$J2, $E2<>"completed", $E2<>"refused", $E2<>"escalated")` | Light orange |
| Time to escalate | `=AND($J2<>"", TODAY()>=$J2, $E2<>"completed", $E2<>"refused", $E2<>"escalated")` | Light red |

## Statuses

| Status | Meaning |
| --- | --- |
| `draft` | Written, not sent |
| `sent` | Sent, no reply yet |
| `acknowledged` | The controller confirmed it received the request |
| `identity_requested` | The controller asked you to confirm who you are |
| `extended` | The controller extended the deadline by two months |
| `completed` | Done: data erased or a copy received |
| `refused` | The controller refused; record the reason in `outcome` |
| `escalated` | You complained to a supervisory authority |

A data validation rule on column E (Data → Data validation → Dropdown) keeps
the statuses consistent, so `gdpr-kit due` can read the sheet if you export it
as CSV later.

## Keep the sheet private

The sheet lists the services you use and your contact with them. Do not share
it by link. If you keep it in Google Drive, it is subject to your Google
account's security; a local file or an encrypted folder is the more private
choice.
