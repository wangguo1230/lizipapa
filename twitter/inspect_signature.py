import inspect
from playwright.async_api import Browser

print(inspect.signature(Browser.new_context))
