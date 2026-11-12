# Evidencias pendientes (no inventar resultados)

- RDS instance: MultiAZ=True and initial primary AvailabilityZone, plus after failover.
- Continuous transfers during failure / recovery (timestamps of first failed / recovered writes).
- Final balances sum EUR 10,000, all confirmed transfer IDs in database, zero duplicate IDs, mean COMMIT latency.
- DynamoDB table region and 100 items for each of Ireland, Virginia and Tokyo.
- Coordinator JSON/screenshots: complete, Top-2, Top-3, and region down (partial flag).
- Lambda concurrency 0 and subsequent restoration.
- terraform destroy and AWS checks for absence of every deployed resource including IAM role and CloudWatch log groups.

PDF must distinguish observations from planned/expected values. Preserve screenshot originals in docs/capturas/.
