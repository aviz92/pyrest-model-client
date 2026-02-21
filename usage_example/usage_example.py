import os

from custom_python_logger import build_logger, json_pretty_format
from dotenv import load_dotenv
from python_base_toolkit.utils.data_serialization import default_serialize

from pyrest_model_client import RestApiClient, build_header
from pyrest_model_client.base import BaseAPIModel, get_model_fields

load_dotenv()

logger = build_logger(__name__)

TOKEN = os.getenv("TOKEN")
BASE_URL = f'{os.getenv("BASE_URL")}:{os.getenv("PORT")}'

base_url: str = "http://localhost:8000"


class VersionedModelApp(BaseAPIModel):
    release: dict | int
    status: str


class Employee(VersionedModelApp):
    name: str
    description: str | None = None
    department: dict | int | None
    resource_path: str = "employee"


class Department(VersionedModelApp):
    name: str
    description: str | None = None
    resource_path: str = "department"


def main(table_name: str, const_filters: dict[str, str] | None = None) -> None:
    header = build_header(token=TOKEN)

    client = RestApiClient(base_url=base_url, header=header)

    # Example: Get all items from the API (paginated) and convert them to model instances
    item_list = []
    params = const_filters
    while res := client.get(table_name, params=params):  # pylint: disable=W0149
        item_list.extend(get_model_fields(res["results"], model=Employee))

        if not res["next"]:
            break
        params = {"page": res["next"].split("/?page=")[-1]}
    logger.info(f"Response: {json_pretty_format(data=item_list, default=default_serialize)}")


if __name__ == "__main__":
    main(
        table_name="employee",
        # table_name="department",
        const_filters={"release__version": "v1.0.0"},
    )
