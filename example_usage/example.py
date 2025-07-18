from pyrest_model_client import RequestClient, build_header, set_client
from example_usage.models.user import User
from example_usage.models.environment import Environment


def main():
    # Initialize the API client globally for all models
    set_client(
        new_client=RequestClient(
            base_url="http://localhost:8000",
            header=build_header(token="b727d196d8ba9012777d955c49dc895c93d2b886")
        )
    )

    # # Create and save
    # e = User(name="Alice")
    # e.save()
    # print()
    #
    # # Change and save
    # e.name = "Alice Smith"
    # e.save()

    # Find all users
    environments = Environment.find()
    print(environments)


if __name__ == "__main__":
    main()
