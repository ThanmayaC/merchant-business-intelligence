# Payment Failure Operations Guide


**Document type:** Operations troubleshooting guide\
**Version:** 1.0\
**Effective date:** 15 October 2026\


## 1. BANK_TIMEOUT

A bank timeout means the expected response was not received within the
configured time window. Possible contributing factors include delayed
bank responses, temporary service load, or connectivity interruptions.
Operations teams should compare the event timestamp, bank name, and
recent failure rate before drawing conclusions.

## 2. ISSUER_DECLINED

An issuer-declined transaction indicates that the issuing institution
did not approve the request. The platform should preserve the response
code when available. A decline should not automatically be interpreted
as a platform outage.

## 3. INSUFFICIENT_FUNDS

This failure category indicates that the payment could not be completed
because the available account balance was insufficient. It is generally
distinct from a technical connectivity failure.

## 4. NETWORK_ERROR

A network error can occur when communication between components is
interrupted. Engineers should inspect service logs, request identifiers,
and timing information to determine where the interruption occurred.

## 5. LIMIT_EXCEEDED

A limit-exceeded response indicates that a configured transaction or
account limit prevented completion. The relevant limit type should be
confirmed from the authoritative response or account configuration.

## 6. Investigation checklist

1.  Identify the affected merchant and time window.
2.  Calculate the failure rate using transaction records.
3.  Group failures by failure reason and bank.
4.  Compare the affected period with an earlier baseline.
5.  Check service and bank response logs before assigning a root cause.
6.  Record evidence and uncertainty in the incident summary.

## 7. Interpretation caution

A correlation between a merchant and a failure reason does not, by
itself, prove causation. Do not claim a bank outage or merchant fault
without supporting operational evidence.
