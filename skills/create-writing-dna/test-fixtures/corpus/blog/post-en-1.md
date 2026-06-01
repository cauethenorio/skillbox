# Stop measuring the wrong thing

We shipped a cache layer last quarter. Latency dropped 40%. Everyone cheered.

Then support tickets went up. Turns out we were serving stale prices to about 3% of users. Fast and wrong.

This happens a lot. You pick a metric because it's easy to graph, not because it's the thing you actually care about. P50 latency looks great on a dashboard. It tells you nothing about the one customer who saw the wrong number and churned.

So here's the rule I use now. Before adding a metric, write down the decision it will change. If you can't name a decision, you don't need the metric. You need a nap.

We rolled the cache back to a 5-second TTL. Latency went up a bit. Tickets went to zero. Boring win. The best kind.
