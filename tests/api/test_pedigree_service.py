import pytest

from utils.integrity import get_all_ancestors


class TestDogsAPI:

    @pytest.mark.testcase("API009")
    def test_get_dog_by_valid_id(self, pedigree_service):
        res = pedigree_service.get_by_id("1")

        assert res.status == 200
        assert isinstance(res.body, dict)
        assert {"id", "breed", "name"} <= res.body.keys()

    @pytest.mark.testcase("API010")
    def test_get_ancestors_valid_dog(self, pedigree_service):
        res = pedigree_service.get_ancestors("1")

        assert res.status == 200
        assert isinstance(res.body["ancestors"], list)
        assert "dog" in res.body
        assert "has_ancestors" in res.body

    @pytest.mark.testcase("API011")
    def test_get_dog_not_found(self, pedigree_service):
        assert pedigree_service.get_by_id("999999").status == 404

    @pytest.mark.testcase("API012")
    def test_get_dog_invalid_id(self, pedigree_service):
        assert pedigree_service.get_by_id("!!!").status in (400, 404)

    @pytest.mark.testcase("API013")
    def test_ancestors_orphan_dog(self, pedigree_service):
        res = pedigree_service.get_ancestors("2")

        assert res.status == 200
        assert res.body["ancestors"] == []
        assert res.body["has_ancestors"] is False

    @pytest.mark.testcase("API014")
    def test_ancestors_not_found_dog(self, pedigree_service):
        assert pedigree_service.get_ancestors("999999").status == 404

    @pytest.mark.testcase("API016")
    def test_no_duplicate_dogs_in_pedigree(self, pedigree_service):
        res = pedigree_service.get_ancestors("120")

        assert res.status == 200

        ids = [d["id"] for d in res.body["ancestors"]]
        assert len(ids) == len(set(ids))

    @pytest.mark.testcase("API017")
    def test_missing_parent_handled_gracefully(self, pedigree_service):
        created_ids = []

        try:
            dogs = [
                {
                    "id": "88881",
                    "name": "BrokenA",
                    "breed": "TestBreed",
                    "sex": "M",
                    "height_cm": 50,
                    "weight_kg": 20,
                    "sire_id": "NO_PARENT_1",
                    "dam_id": None,
                },
                {
                    "id": "88882",
                    "name": "BrokenB",
                    "breed": "TestBreed",
                    "sex": "F",
                    "height_cm": 52,
                    "weight_kg": 21,
                    "sire_id": "NO_PARENT_2",
                    "dam_id": "NO_PARENT_3",
                },
                {
                    "id": "88883",
                    "name": "BrokenC",
                    "breed": "TestBreed",
                    "sex": "M",
                    "height_cm": 53,
                    "weight_kg": 22,
                    "sire_id": None,
                    "dam_id": "NO_PARENT_4",
                },
            ]

            for dog in dogs:
                res = pedigree_service.client.post("/dogs", json=dog)
                assert res.status == 200
                created_ids.append(dog["id"])

            for dog_id in created_ids:
                res = pedigree_service.get_ancestors(dog_id)

                assert res.status == 200
                assert all(a is not None for a in res.body["ancestors"])

                ids = [a["id"] for a in res.body["ancestors"]]
                assert len(ids) == len(set(ids))

        finally:
            for dog_id in created_ids:
                pedigree_service.client.delete(f"/dogs/{dog_id}")

    @pytest.mark.testcase("API018")
    def test_api_pedigree_matches_data_layer(self, pedigree_service, clean_data):
        dog_id = "120"

        res = pedigree_service.get_ancestors(dog_id)
        assert res.status == 200

        api_ids = sorted(d["id"] for d in res.body["ancestors"])
        expected_ids = sorted(get_all_ancestors(clean_data, dog_id, max_depth=5))

        assert api_ids == expected_ids