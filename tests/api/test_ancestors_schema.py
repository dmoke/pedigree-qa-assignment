import pytest
from services.models import AncestorsResponseSchema


class TestAncestorsResponseSchema:

    @pytest.mark.testcase("API001")
    def test_no_ancestors_response_schema(self, pedigree_service):
        res = pedigree_service.get_ancestors("2")
        assert res.status == 200

        response = AncestorsResponseSchema.model_validate(res.body)

        assert response.dog.id == "2"
        assert response.has_ancestors is False
        assert response.ancestors == []

    @pytest.mark.testcase("API002")
    def test_ancestors_response_schema(self, pedigree_service):
        res = pedigree_service.get_ancestors("120")
        assert res.status == 200

        response = AncestorsResponseSchema.model_validate(res.body)

        assert response.dog.id == "120"
        assert response.has_ancestors is True
        assert isinstance(response.ancestors, list)

    @pytest.mark.testcase("API003")
    def test_non_existing_dog_returns_404(self, pedigree_service):
        res = pedigree_service.get_ancestors("999999")
        assert res.status == 404

    @pytest.mark.testcase("API004")
    def test_response_schema_strict_validation(self, pedigree_service):
        res = pedigree_service.get_ancestors("2")
        assert res.status == 200

        AncestorsResponseSchema.model_validate(res.body)