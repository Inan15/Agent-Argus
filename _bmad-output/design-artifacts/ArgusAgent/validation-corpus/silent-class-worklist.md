# Silent-test-class adjudication worklist - Story 16.7

> DERIVED by `scripts/build_silent_class_record.py` from `silent-class-record.json`. Do not hand-edit: re-run the script. Every row below is an **advisory** finding and stays one - this worklist promotes nothing, moves no threshold, and does not touch `adjudication-record.json` or `gate-decision-record.json`.

## THE JUDGEMENT THIS FILE ASKS FOR, AND WHO MAY MAKE IT

**36 row(s) await a named human.** No automated producer may supply the answer: protocol section 2 registers `UNADJUDICATED` as *the ONLY member an automated producer may write*, and *an autonomous story that tags its own findings TP has measured nothing*. Story 16.7 therefore built the instrument, seeded the rows, published this file, and STOPPED.

Registered adjudicators (protocol section 2), for the `adjudicator` field:

- `XAgent007 (Engineering Lead)` - primary adjudicator.
- `Veer Pratap Singh (QA Lead)` - second reviewer, role FILLED 2026-08-22 by operator act.
- **External adjudicator - UNFILLED.** Protocol section 4's ladder is three steps: (1) re-examine the locator, (2) correct the golden key and re-run, (3) external tie-break. Only PERSISTENT DISAGREEMENT between the two filled roles reaches step 3, and a run that reaches it must STOP and report the rows rather than resolve them by default. A `BORDERLINE` on its own is NOT step 3 - it is a first-class recorded outcome meaning *looked at, could not decide*.

Each row needs FOUR things, and the row's constructor refuses anything less:

1. a `disposition` from `BORDERLINE`, `FP`, `TP`, `UNADJUDICATED`;
2. an `idiom` from `DELIBERATE_SMOKE_TEST`, `NOT_ASSESSED`, `NOT_A_SMOKE_TEST` - a SEPARATE axis from the disposition, so a row may be `FP` **and** `DELIBERATE_SMOKE_TEST` at once, and that combination is the measurement;
3. an `adjudicator` id of the exact form `<who> (<role>)`; and
4. an `adjudicated_on` date and a `reason` - a judgement with no reason cannot
   be re-examined, and section 4's ladder IS a re-examination procedure.

## THE CLASS

`V2 SILENT: the flagged test span reaches the system under test and DISCARDS at least one result (discarded_sut_calls >= 1, fact (b)'s own arithmetic, frozen table), AND the span asserts NOTHING AT ALL under the WIDE assertion vocabulary (no bare assert opens any line of the span, and no callee on any edge of the span is a registered assertion name). Measured at HEAD over the 1,032 recorded vacuous_test_heuristic findings: 36 members. NOTE for anyone who later proposes promoting this predicate: V2 is NOT a relaxation of shipped fact (b). V1 (drop the provably-dead mock-referencing clause) reaches 6, V3 (V1 AND silent) also reaches 6, so V1 is a SUBSET of V2 and 30 of the 36 lie outside V1 entirely — 30 members have at least one CONSUMED SUT call, one of them thirteen, which no clause removal from fact (b) can ever reach. Promoting V2 would be a genuinely DIFFERENT predicate, not a loosening.`

By corpus member: **agent-smith** 22, **minions** 14 - across 10 file(s) in agent-smith, 9 file(s) in minions.

Exhaustiveness: UNEVALUABLE — 36 of 36 emitted finding(s) carry no live TP/FP disposition (protocol §4 requires the FULL populated corpus, not a sample). What would close the gap: the named human (protocol §2) adjudicates each residual finding at its cited locator; 0 finding(s) carry a live human disposition and 36 do NOT

Smoke-test proportion: NOT MEASURED — 0 of 36 member(s) have had the idiom question assessed, so there is no denominator. This is refused rather than reported as 0/36: a proportion over rows nobody read is not a measurement (AI-E11-1), and measuring this proportion is the whole purpose of Story 16.7.

Expert hours: expert-hours NOT RECORDED: no adjudication run has taken place, so there are no actual hours to compare against §3's <= 4 expert-hour ceiling. A zero here would claim the work took no time rather than that it has not happened.

Independence of THIS record: adjudication independence: NOT_ESTABLISHED — NO live human judgement is recorded, so independence is UNOBSERVABLE rather than absent — nothing was judged, and 'nobody judged it' is not the same finding as 'the author judged all of it' (AI-E11-1); judged by NOBODY — no live human judgement is recorded; registered protocol §2 role(s) that authored NO live judgement here: Engineering Lead, QA Lead, External adjudicator (a claim about THIS adjudication run and NOT about protocol §2's roster, which is not read here: a registered role may be FILLED and have authored nothing on this record)

Triage colour, and it is NOT a judgement: 18 of 36 span(s) contain a comment character somewhere in the span. That is a fact about punctuation and has no established relationship to intent. It does not seed the `idiom` field, it does not default it, and it does not order this worklist - the rows below are sorted by member and locator only (`DN-16-7-5`).

> SOURCE-SPAN CARVE-OUT, stated rather than assumed. NFR-S1 forbids a source byte from a corpus member appearing in a committed artifact. This worklist carries them anyway, as a BOUNDED and deliberate exception, because the judgement it asks for cannot be made without reading the test: the whole point of the artifact is that the named human does not have to clone five repositories to answer 36 questions. The bound, exactly: (1) spans appear in THIS Markdown file and nowhere else - the machine record carries no source byte at all, and no span is copied into deferred-work.md, into the story file, or into any commit message; (2) every span is read from the member's PINNED BLOB at the sha named on its row, proved against the pin by blob hash, never from a working tree; (3) each span is bounded to the flagged test function and to nothing around it; (4) any span the shipped hardcoded-secret detector flags is REDACTED to its locator and the redaction is recorded on the row.

## agent-smith - 22 member(s) of the silent class

Pin `9ab774d7bf5d61da552c61094b2d478f72dfbb6d`

### `agentsmith-core/tests/test_compiler.py:262` - `test_compiler_taint_tracking_success`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `084b1d3e099e.0`

```python
def test_compiler_taint_tracking_success():
    compiler = WorkflowCompiler()

    # LLM node outputs tainted variable 'user_data', which passes through a HUMAN_APPROVAL gate to clear taint
    spec_with_gate = {
        "metadata": {"name": "taint-success-gate"},
        "graph": [
            {
                "id": "llm_node",
                "operation": "LLM_CALL",
                "outputs": ["user_data"],
                "transitions": [{"next": "gate_node"}]
            },
            {
                "id": "gate_node",
                "operation": "HUMAN_APPROVAL",
                "transitions": [{"next": "mutate_node"}]
            },
            {
                "id": "mutate_node",
                "operation": "WRITE_RECORD",
                "inputs": ["user_data"],
                "parameters": {"table": "accounts"},
                "transitions": [{"next": "end"}],
                "compensation": {"action": "delete"}
            },
            {
                "id": "end",
                "operation": "TERMINAL",
                "parameters": {"status": "SUCCESS"},
                "transitions": []
            }
        ]
    }
    compiler.compile(spec_with_gate)
```

### `agentsmith-core/tests/test_contracts.py:182` - `test_manifest_schema_with_model_pin`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `a9ba4aa2cad3.0`

```python
def test_manifest_schema_with_model_pin():
    manifest_schema = _load_schema("manifest.schema.json")
    valid_manifest = {
        "apiVersion": "agentsmith/v1alpha1",
        "metadata": {
            "name": "test-manifest",
            "ontology_version": "core-ops/1.4.0"
        },
        "capability_summary": {
            "egress_domains": [],
            "database_access": [],
            "non_compensable_actions": [],
            "hitl_gates": []
        },
        "graph": [
            {
                "id": "start",
                "operation": "READ_RECORD"
            }
        ],
        "model_pin": {
            "provider": "openai",
            "model": "gpt-4o",
            "version": "1.0.0",
            "policy": "quarantine"
        }
    }
    # Should validate successfully
    validate(instance=valid_manifest, schema=manifest_schema)
```

### `agentsmith-core/tests/test_contracts.py:213` - `test_trust_report_schema_with_model_drift`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `c78e894a836b.0`

```python
def test_trust_report_schema_with_model_drift():
    trust_schema = _load_schema("trust-report.schema.json")
    valid_report = {
        "schema_version": "1.0",
        "brand": "test-brand",
        "agent_ref": "test-agent",
        "generated_at": "2026-06-26T20:00:00Z",
        "nonce": "test-nonce",
        "epistemic_status": "self-generated, cryptographically self-verifiable; not a third-party audit.",
        "business_legible_twin": {
            "dollars_at_stake": 1000.0,
            "dollars_at_stake_currency": "USD",
            "dollars_at_stake_basis": "declared money-moving step amount",
            "is_declared_input": True,
            "blast_radius_plain_english": "Test blast radius."
        },
        "claims": [],
        "vsaq_assessments": [],
        "enforcement_bounds": {
            "none_enforced": True,
            "enforced_bounds": [],
            "deferred_bounds": {}
        },
        "cryptographic_backing": {
            "ledger_head_hash": None,
            "chain_anchor": None,
            "signing_trigger": "test-trigger"
        },
        "model_drift": {
            "policy_action": "downgrade",
            "pinned": {
                "provider": "openai",
                "model": "gpt-4o",
                "version": "1.0.0"
            },
            "actual": {
                "provider": "anthropic",
                "model": "claude-opus-4-8",
                "version": "2.0.0"
            }
        }
    }
    # Should validate successfully
    validate(instance=valid_report, schema=trust_schema)
```

### `agentsmith-core/tests/test_contracts.py:783` - `test_pre_16_1_wir_without_new_fields_still_validates`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `34b8100f62c2.0`

```python
def test_pre_16_1_wir_without_new_fields_still_validates():
    """AC-2/AC-6 (additive-not-breaking): an existing pre-16-1 WIR that lacks
    is_lossy / constitution_overlay / faithfulness still validates unchanged."""
    wir_schema = _load_schema("wir.schema.json")
    pre_16_1_wir = {
        "name": "legacy-wir",
        "graph": [
            {
                "id": "start",
                "operation": "READ_RECORD",
                "status": "Validated",
                "provenance": {"source": "human"},
            }
        ],
    }
    validate(instance=pre_16_1_wir, schema=wir_schema)
```

### `agentsmith-core/tests/test_contracts.py:903` - `test_16_1_pre_change_manifest_at_1_4_0_still_schema_valid`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `cfc6a8c6ad44.0`

```python
def test_16_1_pre_change_manifest_at_1_4_0_still_schema_valid():
    """AC-4: an existing signed manifest stamped at the OLD ontology_version
    (core-ops/1.4.0) is still schema-valid after the bump — version-aware reading,
    no re-stamp. (ontology_version is a free string in manifest.schema.json, so the
    bump never breaks validation of an older signed manifest.)"""
    manifest_schema = _load_schema("manifest.schema.json")
    legacy_signed_manifest = {
        "apiVersion": "agentsmith/v1alpha1",
        "metadata": {"name": "legacy-signed", "ontology_version": "core-ops/1.4.0"},
        "capability_summary": {
            "egress_domains": [],
            "database_access": [],
            "non_compensable_actions": [],
            "hitl_gates": [],
        },
        "graph": [{"id": "start", "operation": "READ_RECORD"}],
    }
    validate(instance=legacy_signed_manifest, schema=manifest_schema)
```

### `agentsmith-core/tests/test_guarantee_backcompat.py:71` - `test_guarantee_level_admitted_on_all_surfaces`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=3` · row id `9e65370c0aa6.0`

```python
def test_guarantee_level_admitted_on_all_surfaces():
    wir_schema = _load_schema("wir.schema.json")
    doc = json.loads(json.dumps(SPIKE_WIR))
    doc["guarantee_level"] = "by_construction"               # document surface
    doc["graph"][0]["guarantee_level"] = "observed"          # node surface
    doc["graph"][0]["transitions"][0]["guarantee_level"] = "enforced"  # edge surface
    validate(instance=doc, schema=wir_schema)
```

### `agentsmith-core/tests/test_hybrid_composition.py:381` - `test_hybrid_report_validates_against_existing_trust_report_schema`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=13` · row id `241660508998.0`

```python
def test_hybrid_report_validates_against_existing_trust_report_schema():
    """Task 4: the mixed-rung report rides the EXISTING trust-report.schema.json.

    NO new /contracts schema is added — the per-region guarantee_level serializes
    via the existing closed-enum field. Confirms the default posture holds.
    """
    summary, ledger, anchors = make_observed_inputs()
    outer = make_observed_wir()
    egress_id = next(nid for nid in outer.nodes if nid.startswith("egress"))
    hybrid = compose_hybrid_wir(outer, sub_flow=FixtureVerifiedSubFlow(), attach_to=egress_id)
    regions = derive_by_construction_regions(hybrid)
    report = generate_trust_report(
        summary,
        ledger,
        brand="Maya AI Inc.",
        agent_ref="invoice-charge-agent",
        generated_at="2026-06-13T02:00:00Z",
        nonce="nonce-abc",
        dollars_at_stake=250000.0,
        enforced_facets=make_enforced_facets(),
        by_construction_regions=regions,
        anchored_hashes=anchors,
    )
    schema = json.loads((_CONTRACTS_DIR / "trust-report.schema.json").read_text())
    Draft7Validator(schema).validate(report.to_payload())
```

### `agentsmith-core/tests/test_observe_network_proxy.py:122` - `test_summary_validates_against_9_1_schema`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=2` `consumed_sut_calls=3` · row id `1dd84a8ef116.0`

```python
def test_summary_validates_against_9_1_schema():
    observer = NetworkProxyObserver()
    fixture_agent_traffic(observer)
    summary = observer.build_summary("invoice-charge-agent", WINDOW_START, WINDOW_END, run_count=3)
    schema = _load_schema("observed-activity-summary.schema.json")
    validate(instance=summary, schema=schema)  # raises on failure
```

### `agentsmith-core/tests/test_regression_alarm.py:376` - `test_engine_hook_swallows_a_forced_alarm_producer_error`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=4` · row id `c80e035a6b79.0`

```python
def test_engine_hook_swallows_a_forced_alarm_producer_error():
    """A forced error in the alarm sink must NOT crash the run — best-effort (AC-2)."""

    def _boom(_alarm):
        raise RuntimeError("alarm sink exploded")

    hook = ObserveBehavioralRegradeHook(
        on_alarm=_boom,
        generated_at_factory=lambda: "t",
        nonce_factory=lambda: "n",
        grader=_DowngradingGrader(),
    )
    manifest = _manifest_with_grades({"refund.requires_human_approval": "enforced"})
    # Must NOT raise.
    hook.on_model_drift(
        manifest, ("openai", "gpt-4o", "2024-05"), ("openai", "gpt-4o", "2024-11")
    )
```

### `agentsmith-core/tests/test_regression_alarm.py:460` - `test_live_hook_budget_failclose_swallows_alarm_sink_error_never_crashes`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=5` · row id `01c684001b96.0`

```python
def test_live_hook_budget_failclose_swallows_alarm_sink_error_never_crashes():
    """Even on the budget fail-closed path, a sink error must NOT crash the run
    (best-effort): the breach is handled, the alarm-build is attempted, an exploding
    sink is logged + swallowed."""
    from agentsmith_core.observe.behavioral_battery import BatteryBehavioralGrader
    from agentsmith_core.observe.token_circuit_breaker import (
        TIER_PER_CI_RUN,
        CloudTokenBudgetExceededError,
    )

    class _BudgetBreachingGrader(BatteryBehavioralGrader):
        def grade(self, prior_facets, model):
            raise CloudTokenBudgetExceededError("breach", tier=TIER_PER_CI_RUN)

    def _boom(_alarm):
        raise RuntimeError("alarm sink exploded on the budget path")

    hook = ObserveBehavioralRegradeHook(
        on_alarm=_boom,
        generated_at_factory=lambda: "t",
        nonce_factory=lambda: "n",
        grader=_BudgetBreachingGrader(cloud=True),
    )
    manifest = _manifest_with_grades({"refund.requires_human_approval": "enforced"})
    # Must NOT raise.
    hook.on_model_drift(
        manifest, ("openai", "gpt-4o", "2024-05"), ("openai", "gpt-4o", "2024-11")
    )
```

### `agentsmith-core/tests/test_security.py:129` - `test_validate_db_identifiers_exempts_non_query_nodes`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=3` `consumed_sut_calls=0` · row id `a58b8d62319f.0`

```python
def test_validate_db_identifiers_exempts_non_query_nodes():
    # P2: image/adapter, loop-marker, and empty mappings carry no query and so
    # have no table requirement — they must validate cleanly.
    validate_db_identifiers({"image": "gcr.io/x@sha256:abc", "cost_estimate": 0.1})
    validate_db_identifiers({"cost_estimate": 3.0})
    validate_db_identifiers({})
```

### `agentsmith-core/tests/test_security.py:34` - `test_validate_db_identifiers_accepts_valid_mapping`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=0` · row id `15ba3dac7a84.0`

```python
def test_validate_db_identifiers_accepts_valid_mapping():
    validate_db_identifiers({
        "action": "SELECT",
        "table": "invoices",
        "where": {"id": ":invoice_id"},
        "set": {"status": "paid"},
    })  # should not raise
```

### `agentsmith-core/tests/test_security.py:59` - `test_validate_db_identifiers_allows_absent_and_null_blocks`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=2` `consumed_sut_calls=0` · row id `8dce59883736.0`

```python
def test_validate_db_identifiers_allows_absent_and_null_blocks():
    validate_db_identifiers({"table": "users"})                 # blocks absent
    validate_db_identifiers({"table": "users", "where": None})  # explicit null treated as absent
```

### `agentsmith-core/tests/test_security.py:69` - `test_validate_db_identifiers_accepts_valid_select_list`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=3` `consumed_sut_calls=0` · row id `2439acfa3f56.0`

```python
def test_validate_db_identifiers_accepts_valid_select_list():
    validate_db_identifiers({"table": "users", "select": ["id", "amount"]})  # should not raise
    validate_db_identifiers({"table": "users", "select": []})                # empty projection ok
    validate_db_identifiers({"table": "users", "select": None})              # absent/null ok
```

### `agentsmith-core/tests/test_security.py:98` - `test_validate_db_shape_allows_safe_and_non_destructive`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=4` `consumed_sut_calls=0` · row id `d3bc808ae223.0`

```python
def test_validate_db_shape_allows_safe_and_non_destructive():
    # Filtered UPDATE, plain SELECT, and absent/non-string actions are fine.
    validate_db_shape({"action": "UPDATE", "table": "u", "set": {"s": "1"}, "where": {"id": ":u"}})
    validate_db_shape({"action": "SELECT", "table": "u"})
    validate_db_shape({"table": "u"})            # action absent
    validate_db_shape({"action": None, "table": "u"})  # non-string action ignored
```

### `agentsmith-core/tests/test_trust_report.py:629` - `test_report_validates_against_contracts_schema`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=6` · row id `ca39c73f6cb8.0`

```python
def test_report_validates_against_contracts_schema():
    """Task 6: the deliberate /contracts/trust-report.schema.json validates the report."""
    schema_path = _CONTRACTS_DIR / "trust-report.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    for report in (observed_only_report(), observed_plus_enforced_report()):
        validator.validate(report.to_payload())
```

### `agentsmith-core/tests/test_trust_report.py:639` - `test_signed_report_validates_against_contracts_schema`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=6` · row id `37b27694ded2.0`

```python
def test_signed_report_validates_against_contracts_schema():
    schema_path = _CONTRACTS_DIR / "trust-report.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    signed = sign_trust_report(observed_plus_enforced_report(), customer_kms_key_version=_CUSTOMER_KEY)
    validator.validate(signed.to_payload())
```

### `agentsmith-core/tests/test_ui_emitter.py:92` - `test_ui_emitter_envelope_fit`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=3` · row id `cb3069ee96c5.0`

```python
def test_ui_emitter_envelope_fit() -> None:
    """Task 3: Test that emitter output fits payload.ui_bundle in trust-platform-publish schema."""
    schema = load_contract_schema("trust-platform-publish.schema.json")
    bundle = emit_ui_bundle(assets={"index.html": b"hello"})
    payload = bundle.to_publish_payload()

    envelope = {
        "schema_version": "1.1",
        "event_id": "evt-0001",
        "event_type": "ui_bundle.published",
        "emitted_at": "2026-07-13T00:00:00Z",
        "source": {
            "instance_id": "as-instance-1",
            "deployment_profile": "cloud",
            "compiler_version": "0.1.0",
        },
        "tenant": {"tenant_id": "maya-ai"},
        "agent_ref": "payments-agent",
        "artifact_integrity": {
            "signed_payload_sha256": "a" * 64,
            "signature": "customer-kms-signature-blob",
            "customer_kms_key_version": "customer-kms-v3",
        },
        "payload": {
            "kind": "ui_bundle",
            "ui_bundle": payload,
        },
    }

    # Should validate successfully
    validate(instance=envelope, schema=schema)
```

### `agentsmith-core/tests/test_wir_contracts.py:102` - `test_spike_example_commands_validate`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `c79b7edbf173.0`

```python
def test_spike_example_commands_validate():
    command_schema = _load_schema("command.schema.json")
    for cmd in SPIKE_COMMANDS:
        validate(instance=cmd, schema=command_schema)
```

### `agentsmith-core/tests/test_wir_contracts.py:88` - `test_wir_schema_is_valid_json_schema`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `951740a9c4a5.0`

```python
def test_wir_schema_is_valid_json_schema():
    Draft7Validator.check_schema(_load_schema("wir.schema.json"))
```

### `agentsmith-core/tests/test_wir_contracts.py:92` - `test_command_schema_is_valid_json_schema`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `9cf81fdf1b57.0`

```python
def test_command_schema_is_valid_json_schema():
    Draft7Validator.check_schema(_load_schema("command.schema.json"))
```

### `agentsmith-core/tests/test_wir_contracts.py:98` - `test_spike_example_wir_validates`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `892709b37a70.0`

```python
def test_spike_example_wir_validates():
    validate(instance=SPIKE_WIR, schema=_load_schema("wir.schema.json"))
```

## minions - 14 member(s) of the silent class

Pin `ec63b7293b7036bf910a0d1b5e61aba7dc551526`

### `tests/apaa/test_coverage_ledger.py:239` - `test_no_float_fields_serialize`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=3` · row id `4af52d7c6422.0`

```python
    def test_no_float_fields_serialize(self) -> None:
        # The canonical serializer rejects float; a clean round-trip proves the
        # model carries no float leaves.
        led = CoverageLedger.build(_golden_entries())
        canonical.dumps(led.model_dump())  # must not raise
```

### `tests/apaa/test_recording_schema.py:155` - `test_recording_serializes_clean`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=2` · row id `9d4ccc266d82.0`

```python
    def test_recording_serializes_clean(self) -> None:
        # canonical.dumps rejects float; a clean serialize proves no float leaves.
        canonical.dumps(_golden_recording().model_dump())  # must not raise
```

### `tests/config/test_config_llm.py:356` - `test_missing_provider_module_is_silently_skipped`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `71e71e01996b.0`

```python
    def test_missing_provider_module_is_silently_skipped(self):
        """ImportError for an unimplemented provider should not raise."""
        from minions_core.runtime.runtime_provider import RuntimeProviderRegistry
        from minions_core.app_factory import _register_single_llm_provider

        registry = RuntimeProviderRegistry(
            approved_provider_ids=["nonexistent-xyz"],
            default_provider_id="nonexistent-xyz",
        )
        # Should not raise
        _register_single_llm_provider(registry, "nonexistent-xyz")
```

### `tests/governance/test_gate_policy.py:35` - `test_enforce_accepts_valid_approved_gate`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=2` · row id `a9da01aebdd4.0`

```python
    def test_enforce_accepts_valid_approved_gate(self) -> None:
        engine = GatePolicyEngine()
        evaluation = engine.evaluate(
            gate_name="intent",
            present_artifact_types=["clarification"],
            approval_granted=True,
        )

        engine.enforce(evaluation)
```

### `tests/governance/test_hitl_intent_approval.py:467` - `test_ledger_outage_never_turns_a_recorded_approval_into_a_500`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=3` · row id `692ef1119abd.0`

```python
    def test_ledger_outage_never_turns_a_recorded_approval_into_a_500(self) -> None:
        from minions_core.services.api_app import MinionsApiApp

        class _Broken:
            def append_governance_ledger_event(self, **kwargs):
                raise RuntimeError("ledger down")

        app = MinionsApiApp.__new__(MinionsApiApp)
        app.persistence = _Broken()
        app._emit_intent_approval_ledger_event("R", "intent_approval_granted", {})
```

### `tests/governance/test_policy_threshold_hardening.py:288` - `test_mint_internal_system_token_satisfies_policy_mutator_capability`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=2` · row id `c1b4e3fa2a31.0`

```python
def test_mint_internal_system_token_satisfies_policy_mutator_capability():
    runtime = PolicyRuntime()
    token = mint_internal_system_token(
        role="governance",
        capabilities=("policy-mutator",),
    )
    # Should NOT raise — internal token is a valid policy-mutator credential.
    runtime.update_threshold("quality_floor", 78.0, token=token)
```

### `tests/providers/test_providers_base.py:314` - `test_all_capabilities_present`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `21b4dec9309c.0`

```python
    def test_all_capabilities_present(self):
        t = TestProviderCapabilityEnum()
        t.test_all_five_capabilities_present()
```

### `tests/providers/test_providers_base.py:318` - `test_llm_request`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=2` `consumed_sut_calls=1` · row id `194a9ce27236.0`

```python
    def test_llm_request(self):
        t = TestLLMRequestDataclass()
        t.test_instantiation_required_fields()
        t.test_instantiation_all_fields()
```

### `tests/providers/test_providers_base.py:323` - `test_llm_response`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=1` · row id `5a82edf6eee1.0`

```python
    def test_llm_response(self):
        t = TestLLMResponseDataclass()
        t.test_instantiation()
```

### `tests/providers/test_providers_base.py:327` - `test_dispatch_request_backward_compat`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=3` `consumed_sut_calls=1` · row id `8740dce06a2d.0`

```python
    def test_dispatch_request_backward_compat(self):
        t = TestRuntimeDispatchRequestLLMField()
        t.test_default_llm_request_is_none()
        t.test_explicit_llm_request()
        t.test_dispatch_signature_unchanged()
```

### `tests/providers/test_providers_base.py:333` - `test_protocol_imports`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=5` `consumed_sut_calls=1` · row id `d1975e29a46b.0`

```python
    def test_protocol_imports(self):
        t = TestRuntimeProviderContractProtocol()
        t.test_import_from_providers_base()
        t.test_import_from_minions_core_providers_base()
        t.test_runtime_provider_shim_re_exports()
        t.test_protocol_has_is_healthy()
        t.test_is_healthy_default_returns_true()
```

### `tests/providers/test_providers_base.py:341` - `test_deprecation_warning`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=2` `consumed_sut_calls=1` · row id `4d5478927a99.0`

```python
    def test_deprecation_warning(self):
        t = TestStrCapabilitiesDeprecationWarning()
        t.test_str_capabilities_emit_deprecation_warning()
        t.test_provider_capability_enum_no_deprecation_warning()
```

### `tests/runtime/test_run_index_patrol_escalation.py:84` - `test_escalation_never_raises_even_if_incident_backend_fails`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=4` · row id `5e6d3094df06.0`

```python
def test_escalation_never_raises_even_if_incident_backend_fails():
    """TC-OBS-001-57 — escalation swallows its own failures (must not kill the loop)."""
    incident = _FakeIncidentEngine(raise_on_create=True)
    tracer = _FakeTracer()
    patrol = _patrol(incident, tracer)

    # Must not propagate — a broken incident backend cannot turn a sweep failure
    # into a loop-killer.
    patrol.escalate_sweep_failure(RuntimeError("db locked"))
```

### `tests/test_import_paths.py:225` - `test_component_module_importable`

- disposition: `UNADJUDICATED` · idiom: `NOT_ASSESSED` · adjudicator: `NONE` · date: `NONE`
- measured: `discarded_sut_calls=1` `consumed_sut_calls=0` · row id `626bd471d4a3.0`

```python
def test_component_module_importable(module_name: str) -> None:
    """Every §4a component module imports from its canonical path."""
    importlib.import_module(module_name)
```


_Nothing above is adjudicated. Every row is `UNADJUDICATED` and carries no adjudicator - which is the honest state, and the state protocol section 2 says an automated producer must leave it in._
