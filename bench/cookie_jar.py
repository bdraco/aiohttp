import timeit
from http import cookies

from yarl import URL

from aiohttp import CookieJar


def filter_large_cookie_jar():
    """Filter out large cookies from the cookie jar."""
    jar = CookieJar()
    c = cookies.SimpleCookie()
    domain_url = URL("http://maxagetest.com/")
    other_url = URL("http://otherurl.com/")

    for i in range(5000):
        cookie_name = f"max-age-cookie{i}"
        c[cookie_name] = "any"
        c[cookie_name]["max-age"] = 60
        c[cookie_name]["domain"] = "maxagetest.com"
    jar.update_cookies(c, domain_url)
    assert len(jar) == 5000
    assert len(jar.filter_cookies(domain_url)) == 5000
    assert len(jar.filter_cookies(other_url)) == 0

    filter_domain = timeit.timeit(lambda: jar.filter_cookies(domain_url), number=1000)
    filter_other_domain = timeit.timeit(
        lambda: jar.filter_cookies(other_url), number=1000
    )
    print(f"filter_domain: {filter_domain}")
    print(f"filter_other_domain: {filter_other_domain}")


filter_large_cookie_jar()
