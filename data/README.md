# Merchant Intelligence Assistant — Sample Data

All records and policies in this package are synthetic and fictional, created for interview practice.

## Structured data
- `transactions.csv`: 600 synthetic transaction records.
- `merchants.csv`: 12 synthetic merchant records.

Suggested transaction fields:
`transaction_id`, `merchant_id`, `merchant_name`, `transaction_timestamp`, `amount_inr`, `status`, `payment_method`, `bank_name`, `failure_reason`, `city`.

## Unstructured data
- `merchant_onboarding_policy.md`
- `payment_failure_operations_guide.md`
- `merchant_performance_review_guide.md`

These documents are fictional demo knowledge-base content, not official NPCI, bank, or regulatory policies.

## Suggested tests
- Calculate total transaction count and volume.
- Calculate overall and merchant-wise success rates.
- Find top merchants by transaction volume.
- Retrieve passages about `BANK_TIMEOUT`.
- Ask a semantic question such as: "Why might a payment take too long to receive confirmation?"
- Compare BM25, dense retrieval, and RRF rankings.
