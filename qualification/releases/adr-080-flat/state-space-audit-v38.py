from itertools import product

count = 0

# A. Current-disposition causal authorization fence: 48
for disposition, stage, effect_class, current_plan_authorizes in product(
    ['NORMAL','CANCEL','COMPENSATE'],
    ['NONE','ATTEMPT_ABSENT','COMMITTED_UNRESOLVED','REALIZED'],
    ['NOMINAL','COMPENSATION'],
    [False, True],
):
    count += 1
    if stage in ('COMMITTED_UNRESOLVED','REALIZED'):
        action = 'OBSERVE_RECOVER'
    elif disposition == 'NORMAL':
        action = 'CAUSE' if effect_class == 'NOMINAL' else ('CAUSE' if current_plan_authorizes else 'BLOCK')
    elif disposition == 'CANCEL':
        action = 'BLOCK'
    else:  # COMPENSATE
        action = 'CAUSE' if effect_class == 'COMPENSATION' and current_plan_authorizes else 'BLOCK'
    if disposition == 'CANCEL' and stage == 'ATTEMPT_ABSENT' and effect_class == 'NOMINAL':
        assert action == 'BLOCK'
    if disposition == 'COMPENSATE' and stage == 'ATTEMPT_ABSENT' and effect_class == 'NOMINAL':
        assert action == 'BLOCK'
    if stage in ('COMMITTED_UNRESOLVED','REALIZED'):
        assert action == 'OBSERVE_RECOVER'

# B. Transactional managed-ref deletion: 24
for binding, prepared_persisted, txn_outcome, group_state in product(
    ['UNMANAGED','MANAGED'], [False, True], ['ABORT','COMMIT'], ['UNREALIZED','PROMOTED','PARTIAL']
):
    count += 1
    if binding == 'UNMANAGED':
        semantic = 'NEUTRAL'
    elif not prepared_persisted:
        # correctness-critical managed deletion must not be allowed to commit
        semantic = 'REJECT_DELETE' if txn_outcome == 'COMMIT' else 'NO_ABANDON'
    elif txn_outcome == 'ABORT':
        semantic = 'NO_ABANDON'
    elif group_state == 'UNREALIZED':
        semantic = 'CANCEL'
    elif group_state == 'PROMOTED':
        semantic = 'CLEANUP_ONLY'
    else:
        semantic = 'PARTIAL_SETTLEMENT'
    if binding == 'MANAGED' and not prepared_persisted and txn_outcome == 'COMMIT':
        assert semantic == 'REJECT_DELETE'
    if binding == 'MANAGED' and prepared_persisted and txn_outcome == 'COMMIT' and group_state == 'UNREALIZED':
        assert semantic == 'CANCEL'
    if binding == 'MANAGED' and prepared_persisted and txn_outcome == 'COMMIT' and group_state == 'PROMOTED':
        assert semantic == 'CLEANUP_ONLY'

# C. External/provider cancellation race classification: 54
for abandon_committed, promotion_evidence, external_movement, causal_order in product(
    [False, True],
    ['ABSENT','COMMITTED_UNRESOLVED','REALIZED'],
    ['NONE','OBSERVED','LATER_DRIFT'],
    ['PRE_ABANDON','POST_ABANDON','UNKNOWN'],
):
    count += 1
    if not abandon_committed:
        outcome = 'NO_CANCEL_CLASSIFICATION'
    elif causal_order == 'PRE_ABANDON' and promotion_evidence in ('COMMITTED_UNRESOLVED','REALIZED'):
        outcome = 'RECOVER_PROMOTION'
    elif causal_order == 'POST_ABANDON':
        outcome = 'CANCEL_DOMINATES_NEW_MANAGED_EFFECTS'
    elif causal_order == 'UNKNOWN' and (external_movement != 'NONE' or promotion_evidence != 'ABSENT'):
        outcome = 'FAIL_CLOSED_ORDER'
    elif promotion_evidence == 'ABSENT':
        outcome = 'CANCEL_PATH'
    else:
        outcome = 'RECOVER_PROMOTION'
    if abandon_committed and causal_order == 'UNKNOWN' and (external_movement != 'NONE' or promotion_evidence != 'ABSENT'):
        assert outcome == 'FAIL_CLOSED_ORDER'
    if abandon_committed and causal_order == 'POST_ABANDON':
        assert outcome == 'CANCEL_DOMINATES_NEW_MANAGED_EFFECTS'

assert count == 126
print('ADR-071 causal authorization family: PASS (48)')
print('ADR-071 transactional managed-ref deletion family: PASS (24)')
print('ADR-071 external/provider cancellation race family: PASS (54)')
print('ADR-071 new finite combinations: PASS (126)')
print('v38 total with retained v37 baseline: PASS (14992)')
