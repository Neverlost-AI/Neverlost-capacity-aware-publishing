# Recovery-Aware Resume Checkpoint

**Artifact:** `recovery-aware-synthetic-demo-v0.1`  
**Status:** `REVIEW_ONLY_CHECKPOINT_SAVED`  
**Profile:** `recovery`  
**User-selected active-minute budget:** 8.0

> This is session-planning information supplied by the creator. It is not a medical, disability, or work-capacity determination.

## Completed mechanical tasks

- `build_captions`
- `build_qa`
- `render_media`
- `start_build`

## Scheduled for this session

- Review the visual contact sheet (4.0 active min)
- Spot-check captions against narration (2.0 active min)

## Preserved for a later session

- Approve title, description, and platform copy (3.0 active min)
- Upload the approved media package (2.0 active min)
- Make the final publication decision (1.0 active min)

## Exact next step

Approve title, description, and platform copy

To regenerate the plan without rebuilding media:

```bash
python build_short.py --manifest manifests/recovery_aware_synthetic_demo.json --capacity-profile recovery --capacity-budget 8.0 --plan-only
```

## Estimate boundary

Workflow estimates for planning; not measured user outcomes. Publication remains a separate human action.
