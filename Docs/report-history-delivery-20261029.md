# Historical report delivery recovery

The public site previously copied only the latest Work report and limited research pages to recent runs. Minute overlays displaced completed daily reports. The October 23 US Work draft also remained pending after its fresh publication window expired.

The site now provides a validated 30-day Work history and completed daily analysis history. Exact archived JSON bytes and original analysis/publication clocks remain intact. Partial failures retain their actual status and counts. Invalid, future-dated, unbound or secret-bearing reports are excluded.

`tradingagents.work publish --historical` explicitly archives a pending, packet-bound market draft for historical reading. It requires timezone-aware source clocks and non-executable strategies/actions, retains packet coverage and schema validation, and writes only `historical-events`. It never updates latest, pending delivery fields, or ACK state. Ordinary fresh publication remains unchanged.

`tradingagents.local_automation publish --reports-only` uses the existing publication lock and requires a verified, unchanged committed site and unchanged canonical latest market reports. Independently published YouTube/PRISM reports can advance through the existing content-addressed validation; their arrival does not block historical delivery. It adds historical pages using the normal sanitizing renderers, snapshot/branch rollback guards, and exact live delivery verification. It preserves the prior research fingerprint so newly arrived research is not falsely marked rebuilt. The original publisher remains responsible for those new inputs.
