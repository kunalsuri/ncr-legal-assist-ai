from src.generation.verifier import verify_answer


def test_valid_citation():
    ok, fab = verify_answer("The Act says X [dl-tenancy-deposit-recovery, S.27].",
                            {"dl-tenancy-deposit-recovery"})
    assert ok and fab == []


def test_fabricated_citation():
    ok, fab = verify_answer("The Act says X [fake-article-id, S.99].", set())
    assert not ok
    assert fab == ["fake-article-id"]


def test_no_citation_fails():
    ok, fab = verify_answer("The Act says X.", {"dl-tenancy-deposit-recovery"})
    assert not ok
