This automation runs every two weeks, anchored to Friday <ANCHOR_DATE>. The trigger fires weekly, so gate first: run `python3 -c "import datetime as d; print((d.date.today() - d.date(<ANCHOR_YEAR>, <ANCHOR_MONTH>, <ANCHOR_DAY>)).days % 14)"` and stop without posting unless it prints 0. If the command itself fails, post that failure instead of stopping.

Using the GitHub API and the GH_TOKEN environment variable, retrieve the following metrics for the last 2 weeks (from 2 weeks ago Friday excluded to today Friday included):

**Dev Team Metrics:**
1. Count new P0 bugs: Use search query `is:issue label:P0 -label:Support created:>=YYYY-MM-DD -reason:"not planned"` (set date to 2 weeks ago). For these P0 bugs, read the corresponding issues and include a one-line summary of pain+impact+status of each in this section.
2. Count fixed bugs: Use search query `is:issue is:closed label:Bug,Chore -label:Stale -label:Support closed:>=YYYY-MM-DD -reason:"not planned"` (set date to 2 weeks ago)
3. Count total open bugs: Use search query `is:issue is:open sort:updated-desc label:Bug`

**Support Metrics:**
1. Count total open support issues: Use search query `is:issue is:open label:Support`
2. Count fixed support issues: Use search query `is:issue is:closed label:Support -label:Stale closed:>=YYYY-MM-DD -reason:"not planned"` (set date to 2 weeks ago)

Format the results as a clear biweekly KPI report and send to the team chat with these metrics organized in two sections by team (Dev Team and Support). Include the date range in the report. Do not include how you obtained them. You may add a qualitative conclusion if it is relevant, otherwise skip it.
