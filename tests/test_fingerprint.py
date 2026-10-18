import pytest
from agent_browser_mesh.fingerprint import (
    create_semantic_anchor,
    AnchorRegistry,
    generate_fingerprint_hash
)


def test_anchor_creation_and_hash_stability():
    anchor1 = create_semantic_anchor(tag="button", role="button", text="Checkout Now")
    anchor2 = create_semantic_anchor(tag="button", role="button", text="Checkout Now")
    assert anchor1.fingerprint_hash == anchor2.fingerprint_hash
    assert anchor1.anchor_id == anchor2.anchor_id
    assert "@butt-checkout-now-" in anchor1.anchor_id


def test_anchor_registry_exact_and_fuzzy_resolution():
    registry = AnchorRegistry()
    btn = create_semantic_anchor(tag="button", role="button", text="Complete Purchase")
    inp = create_semantic_anchor(tag="input", input_type="email", aria_label="Your Work Email")

    registry.register(btn)
    registry.register(inp)

    # 1. Exact ID match
    resolved_btn = registry.resolve(btn.anchor_id)
    assert resolved_btn is not None
    assert resolved_btn.text == "Complete Purchase"

    # 2. Fuzzy text match
    resolved_fuzzy = registry.resolve("purchase")
    assert resolved_fuzzy is not None
    assert resolved_fuzzy.anchor_id == btn.anchor_id

    # 3. Fuzzy aria match
    resolved_aria = registry.resolve("work email")
    assert resolved_aria is not None
    assert resolved_aria.anchor_id == inp.anchor_id

    # 4. Unknown query
    assert registry.resolve("non_existent_element_xyz") is None
