import json

import pytest

from server import (
    max_place_for_booking,
    booking_is_allowed,
    save_competition_table,
    save_club_table,
    save_booking_table,
    save_booking,
)
from tests.conftest import (
    refresh_datafiles,
    DATABASE_DIRECTORY_FOR_TEST,
    COMPETITIONS_TABLE,
    CLUBS_TABLE,
    BOOKINGS_TABLE,
)


class TestUnitServerBookPlacesClass:

    #  "number_of_places_competition, points_club, total_booked_places, expected"
    max_place_for_booking_datas = [
        (25, 11, 11, 1),  # test MAX_PLACE_PER_BOOKING
        (25, 11, 0, 3),  # test club's points
        (25, 64, 0, 12),  # test MAX_PLACE_PER_BOOKING
        (5, 24, 12, 0),  # test MAX_PLACE_PER_BOOKING
        (5, 24, 0, 5),  # test competition's places
        ("5", 14, 0, 0),  # test type error
        (5, "14", 0, 0),  # test type error
        (5, 14, "0", 0),  # test type error
    ]
    # "places_required, number_of_places, club_points,total_booked_places,date_competition, expected",
    booking_is_allowed_datas = [
        (
            1,
            25,
            11,
            11,
            "2050-10-22 13:30:00",
            (True, "booking must be save"),
        ),  # test MAX_PLACE_PER_BOOKING => eq
        (
            3,
            25,
            11,
            0,
            "2050-10-22 13:30:00",
            (True, "booking must be save"),
        ),  # test club's points => eq
        (
            12,
            25,
            64,
            0,
            "2050-10-22 13:30:00",
            (True, "booking must be save"),
        ),  # test MAX_PLACE_PER_BOOKING => eq
        (
            0,
            5,
            24,
            12,
            "2020-10-22 13:30:00",
            (False, "booking must be superior to 0"),
        ),  # test places required <= 0
        (
            5,
            5,
            24,
            0,
            "2050-10-22 13:30:00",
            (True, "booking must be save"),
        ),  # test competition's places => eq
        (
            0,
            "5",
            14,
            0,
            "2020-10-22 13:30:00",
            (False, "booking must be superior to 0"),
        ),  # test type error => eq
        (
            0,
            5,
            "14",
            0,
            "2020-10-22 13:30:00",
            (False, "booking must be superior to 0"),
        ),  # test type error => eq
        (
            0,
            5,
            14,
            "0",
            "2020-10-22 13:30:00",
            (False, "booking must be superior to 0"),
        ),  # test type error => eq
        (
            0,
            25,
            5,
            11,
            "2025-10-22 13:30:00",
            (False, "booking must be superior to 0"),
        ),  # # test places required <= 0
        (
            4,
            25,
            25,
            0,
            "2050-10-22 13:30:00",
            (True, "booking must be save"),
        ),  # test club's points => inf
        (
            11,
            25,
            64,
            0,
            "2050-10-22 13:30:00",
            (True, "booking must be save"),
        ),  # test MAX_PLACE_PER_BOOKING => inf
        (
            4,
            25,
            14,
            0,
            "2050-10-22 13:30:00",
            (True, "booking must be save"),
        ),  # test competition's places => inf
        (
            2,
            25,
            5,
            11,
            "2050-10-22 13:30:00",
            (False, "enter less places!"),
        ),  # test MAX_PLACE_PER_BOOKING => sup
        (
            6,
            25,
            5,
            0,
            "2020-10-22 13:30:00",
            (False, "enter less places!"),
        ),  # test club's points => sup
        (
            13,
            25,
            14,
            0,
            "2020-10-22 13:30:00",
            (False, "enter less places!"),
        ),  # test MAX_PLACE_PER_BOOKING => sup
        (
            1,
            5,
            14,
            12,
            "2020-10-22 13:30:00",
            (False, "enter less places!"),
        ),  # test MAX_PLACE_PER_BOOKING => sup
        (
            6,
            5,
            14,
            0,
            "2020-10-22 13:30:00",
            (False, "enter less places!"),
        ),  # test competition's places => sup
        (
            1,
            "5",
            14,
            0,
            "2020-10-22 13:30:00",
            (False, "enter less places!"),
        ),  # test type error => sup
        (
            1,
            5,
            "14",
            0,
            "2020-10-22 13:30:00",
            (False, "enter less places!"),
        ),  # test type error => sup
        (
            1,
            5,
            14,
            "0",
            "2020-10-22 13:30:00",
            (False, "enter less places!"),
        ),  # test type error => sup
        (
            4,
            5,
            14,
            0,
            "2020-10-22 13:30:00",
            (False, "too late the competition is over"),
        ),  # test the competition is over
    ]

    def setup_method(self):
        refresh_datafiles()

    @pytest.mark.parametrize(
        "number_of_places_competition, points_club, total_booked_places, expected",
        max_place_for_booking_datas,
    )
    def test_max_place_for_booking(
        self, number_of_places_competition, points_club, total_booked_places, expected
    ):
        max_places = max_place_for_booking(
            number_of_places_competition, points_club, total_booked_places
        )
        assert max_places == expected

    @pytest.mark.parametrize(
        "places_required, number_of_places, club_points,total_booked_places,date_competition, expected",
        booking_is_allowed_datas,
    )
    def test_booking_is_allowed(
        self,
        places_required: int,
        number_of_places: int,
        club_points: int,
        total_booked_places: int,
        date_competition: str,
        expected,
    ):
        is_allowed = booking_is_allowed(
            places_required,
            number_of_places,
            club_points,
            total_booked_places,
            date_competition,
        )
        assert is_allowed == expected

    def test_save_competition_table(self, app, mocker, competition_fixture):
        mocker.patch("server.app", app)
        competition_fixture[0].update({"date": "2050-10-22 13:30:00"})
        save_competition_table(competition_fixture[0], 2)
        file_path = f"{DATABASE_DIRECTORY_FOR_TEST}{COMPETITIONS_TABLE}.json"
        with open(file_path) as c:
            list_dataset = json.load(c)[COMPETITIONS_TABLE]

        assert list_dataset == [
            {
                "name": "competition test1",
                "date": "2020-03-27 10:00:00",
                "numberOfPlaces": "6",
            },
            {
                "name": "competition test2",
                "date": "2050-10-22 13:30:00",
                "numberOfPlaces": "4",
            },
        ]

    def test_save_club_table(self, app, mocker, club_fixture):
        mocker.patch("server.app", app)
        save_club_table(club_fixture[0], 2)
        file_path = f"{DATABASE_DIRECTORY_FOR_TEST}{CLUBS_TABLE}.json"
        with open(file_path) as c:
            list_dataset = json.load(c)[CLUBS_TABLE]

        assert list_dataset == [
            {"name": "test1", "email": "test1@project11.fr", "points": "7"},
            {"name": "test2", "email": "test2@project11.fr", "points": "4"},
            {"name": "test3", "email": "test3@project11.fr", "points": "12"},
        ]

    def test_save_booking_table(self, app, mocker, booking_fixture):
        mocker.patch("server.app", app)
        save_booking_table(
            booking_fixture[0]["club"], booking_fixture[0]["competition"], 2
        )
        file_path = f"{DATABASE_DIRECTORY_FOR_TEST}{BOOKINGS_TABLE}.json"
        with open(file_path) as c:
            list_dataset = json.load(c)[BOOKINGS_TABLE]

        assert list_dataset == [
            {"club": "test1", "competition": "competition test2", "booked_places": 2},
            {"club": "test1", "competition": "competition test2", "booked_places": 1},
            {"club": "test1", "competition": "competition test2", "booked_places": 2},
            {"club": "test2", "competition": "competition test2", "booked_places": 5},
            {"club": "test1", "competition": "competition test2", "booked_places": 2},
            {"club": "test1", "competition": "competition test1", "booked_places": 2},
            {"club": "test1", "competition": "competition test2", "booked_places": 2},
        ]

    def test_save_booking(self, app, mocker, club_fixture, competition_fixture):
        mocker.patch("server.app", app)

        result, message = save_booking(club_fixture[0], competition_fixture[0], 0)
        assert result is False
        assert message == "booking must be superior to 0"

        result, message = save_booking(club_fixture[0], competition_fixture[0], 7)
        assert result is False
        assert message == "enter less places!"

        result, message = save_booking(club_fixture[0], competition_fixture[0], 2)
        assert result is False
        assert message == "too late the competition is over"

        competition_fixture[0].update({"date": "2050-10-22 13:30:00"})
        result, message = save_booking(club_fixture[0], competition_fixture[0], 2)
        assert result is True
        assert message == "Great-booking complete!"
