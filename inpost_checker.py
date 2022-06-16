import selenium
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from enum import Enum

__all__ = ["PackageState", "get_package_state"]


class PackageState(Enum):
    DELIVERED = "Dostarczona."
    INBOX = "Umieszczona w Paczkomacie (odbiorczym)."
    IN_DELIVERY = "Przekazano do doręczenia."
    WAREHOUSE = "Przyjęta w oddziale InPost."
    ON_ROUTE = "W trasie."
    RETRIEVED = "Odebrana od klienta."
    PREPARED = "Przygotowana przez Nadawcę."


def get_package_state(package_num: int | str):
    driver = Firefox()
    package_num = str(package_num)
    if len(package_num) != 24:
        raise AttributeError("package_num must be 24 digits long")
    driver.get(f"https://inpost.pl/sledzenie-przesylek?number={package_num}")
    try:
        element = driver.find_element(By.CSS_SELECTOR, "div.-active > div.messageBox > p.-big")
        state = PackageState(element.get_attribute("innerHTML"))
    except (exceptions.NoSuchElementException, exceptions.NoSuchAttributeException):
        raise AttributeError(f"No package with number {package_num} found")
    finally:
        driver.close()
    return state


# print(get_package_state(612240810055040047415041))
# print(get_package_state(123456789012345678901234))