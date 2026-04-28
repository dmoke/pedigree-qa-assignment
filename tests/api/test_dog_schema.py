import pytest

from services.models import DogSchema


class TestDogSchema:

    @pytest.mark.testcase("API005")
    def test_get_all_dogs_match_schema(self, pedigree_service):
        res = pedigree_service.get_all()

        assert res.status == 200

        for dog in res.body:
            DogSchema(**dog)

    @pytest.mark.testcase("API006")
    def test_get_dog_matches_schema(self, pedigree_service):
        res = pedigree_service.get_by_id("1")

        if res.status == 200:
            DogSchema(**res.body)

    @pytest.mark.testcase("API007")
    def test_non_existing_dog_returns_404(self, pedigree_service):
        res = pedigree_service.get_by_id("999999")
        assert res.status == 404

    @pytest.mark.testcase("API008")
    def test_no_extra_fields_in_dog_response(self, pedigree_service):
        res = pedigree_service.get_by_id("1")

        if res.status == 200:
            allowed = set(DogSchema.model_fields.keys())

            extra = set(res.body.keys()) - allowed
            assert not extra, f"Unexpected fields: {extra}"
