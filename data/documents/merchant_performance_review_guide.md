# Merchant Performance Review Guide


**Document type:** Business analytics guide\
**Version:** 1.1\
**Effective date:** 20 October 2026\


## 1. Core metrics

Transaction count is the number of transaction records in the selected
period. Transaction volume is the sum of transaction amounts for the
selected records. Success rate is successful transaction count divided
by total transaction count, multiplied by 100.

## 2. Merchant comparisons

Merchant comparisons should use the same date range and consistent
status definitions. Very low transaction counts should be highlighted
because small samples can produce volatile percentages.

## 3. Trend analysis

A declining success rate should be investigated by comparing multiple
time windows. Review changes in payment method mix, bank distribution,
failure reasons, and transaction volume. Avoid comparing periods of
substantially different length without normalisation.

## 4. Escalation signals

A sustained decrease in success rate, a sudden increase in BANK_TIMEOUT
or NETWORK_ERROR events, or a material fall in transaction volume may
justify further investigation. These are investigation signals, not
proof of a specific root cause.

## 5. Reporting

Every reported metric should state its date range, denominator, and
relevant filters. Answers should distinguish measured facts from
possible explanations and should identify the source data used.
