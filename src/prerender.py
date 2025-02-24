def get_http_section(config: list) -> dict:
    """
    Returns the http section from the configuration.
    """
    for section in config:
        if section.get("directive") == "http":
            return section
    raise Exception("No http section found in the configuration")


def get_server_block(config: list) -> dict:
    """
    Returns the first server block found in the http section.
    """
    http_section = get_http_section(config)
    for directive in http_section.get("block", []):
        if directive.get("directive") == "server":
            return directive
    raise Exception("No server block found in the http section")

"""
    Returns the location block with the given path in the server block.
"""
def get_location_block(server_block: dict, location: str) -> dict:
    for directive in server_block.get("block", []):
        if directive.get("directive") == "location":
            args = directive.get("args", [])
            if args and args[0] == location:
                return directive
    raise Exception(f"No location block found for {location} in the server block")

def add_map_section(config: list) -> None:
    """
    Adds map directives into the http section before the first server block.
    """
    http_section = get_http_section(config)
    # Find the index of the first server block in the http section
    server_index = None
    for i, directive in enumerate(http_section.get("block", [])):
        if directive.get("directive") == "server":
            server_index = i
            break
    if server_index is None:
        raise Exception("No server directive found in the http section")

    # Build map directive: map $http_user_agent $prerender_ua { ... }
    map_http_user_agent = {
        "directive": "map",
        "args": ["$http_user_agent", "$prerender_ua"],
        "block": [
            {"directive": "default", "args": ["0"]},
            {"directive": "~*Prerender", "args": ["0"]},
            {"directive": "~*googlebot", "args": ["1"]},
            {"directive": "~*yahoo!\\ slurp", "args": ["1"]},
            {"directive": "~*bingbot", "args": ["1"]},
            {"directive": "~*yandex", "args": ["1"]},
            {"directive": "~*baiduspider", "args": ["1"]},
            {"directive": "~*facebookexternalhit", "args": ["1"]},
            {"directive": "~*twitterbot", "args": ["1"]},
            {"directive": "~*rogerbot", "args": ["1"]},
            {"directive": "~*linkedinbot", "args": ["1"]},
            {"directive": "~*embedly", "args": ["1"]},
            {"directive": "~*quora\\ link\\ preview", "args": ["1"]},
            {"directive": "~*showyoubot", "args": ["1"]},
            {"directive": "~*outbrain", "args": ["1"]},
            {"directive": "~*pinterest\\/0\\.", "args": ["1"]},
            {"directive": "~*developers.google.com\\/\\+\\/web\\/snippet", "args": ["1"]},
            {"directive": "~*slackbot", "args": ["1"]},
            {"directive": "~*vkshare", "args": ["1"]},
            {"directive": "~*w3c_validator", "args": ["1"]},
            {"directive": "~*redditbot", "args": ["1"]},
            {"directive": "~*applebot", "args": ["1"]},
            {"directive": "~*whatsapp", "args": ["1"]},
            {"directive": "~*flipboard", "args": ["1"]},
            {"directive": "~*tumblr", "args": ["1"]},
            {"directive": "~*bitlybot", "args": ["1"]},
            {"directive": "~*skypeuripreview", "args": ["1"]},
            {"directive": "~*nuzzel", "args": ["1"]},
            {"directive": "~*discordbot", "args": ["1"]},
            {"directive": "~*google\\ page\\ speed", "args": ["1"]},
            {"directive": "~*qwantify", "args": ["1"]},
            {"directive": "~*pinterestbot", "args": ["1"]},
            {"directive": "~*bitrix\\ link\\ preview", "args": ["1"]},
            {"directive": "~*xing-contenttabreceiver", "args": ["1"]},
            {"directive": "~*chrome-lighthouse", "args": ["1"]},
            {"directive": "~*telegrambot", "args": ["1"]},
            {"directive": "~*google-inspectiontool", "args": ["1"]},
            {"directive": "~*petalbot", "args": ["1"]}
        ]
    }

    # Build map directive: map $args $prerender_args { ... }
    map_args = {
        "directive": "map",
        "args": ["$args", "$prerender_args"],
        "block": [
            {"directive": "default", "args": ["$prerender_ua"]},
            {"directive": "~(^|&)_escaped_fragment_=", "args": ["1"]}
        ]
    }

    # Build map directive: map $http_x_prerender $x_prerender { ... }
    map_http_x_prerender = {
        "directive": "map",
        "args": ["$http_x_prerender", "$x_prerender"],
        "block": [
            {"directive": "default", "args": ["$prerender_args"]},
            {"directive": "1", "args": ["0"]}
        ]
    }

    # Build map directive: map $uri $prerender { ... }
    map_uri = {
        "directive": "map",
        "args": ["$uri", "$prerender"],
        "block": [
            {"directive": "default", "args": ["$x_prerender"]},
            {"directive": "~*\\.(js|css|xml|less|png|jpg|jpeg|gif|pdf|txt|ico|rss|zip|mp3|rar|exe|wmv|doc|avi|ppt|mpg|mpeg|tif|wav|mov|psd|ai|xls|mp4|m4a|swf|dat|dmg|iso|flv|m4v|torrent|ttf|woff|woff2|svg|eot)", "args": ["0"]}
        ]
    }

    # Insert all map directives before the server directive.
    maps_to_insert = [map_http_user_agent, map_args, map_http_x_prerender, map_uri]
    for offset, map_directive in enumerate(maps_to_insert):
        http_section['block'].insert(server_index + offset, map_directive)


def add_rewrite_to_root_server_location(config: list) -> None:
    server_block = get_server_block(config)
    location_root_block = get_location_block(server_block, "/")

    # Define the if block directive
    if_block = {
        "directive": "if",
        "args": ["($prerender = 1)"],
        "block": [
            {"directive": "rewrite", "args": ["(.*)", "/prerenderio", "last"]}
        ]
    }

    # Ensure the location block has a block for nested directives
    location_root_block.setdefault("block", []).append(if_block)

"""
location / {
    if ($prerender = 1) {
        rewrite (.*) /prerenderio last;
    }
    ...
}
"""
def php_rewire_root_location(config):
    server_block = get_server_block(config)
    location_root_block = get_location_block(server_block, "/")

    # Define the if block directive
    if_block = {
        "directive": "if",
        "args": ["$prerender", "=", "1"],
        "block": [
            {"directive": "rewrite", "args": ["(.*)", "/prerenderio", "last"]}
        ]
    }

    # Define the rewrite block directive
    rewrite_block = {
        "directive": "rewrite",
        "args": ["(.*)", "/index.php$1", "last"]
    }

    # prepend the if block directive to the location block
    location_root_block.setdefault("block", []).insert(0, if_block)



def add_location_prerenderio(config: list) -> None:
    """
    Inserts a new location block for "/prerenderio" into the first server block.
    """
    server_block = get_server_block(config)

    # Locate the index of the location "/" block within the server block.
    location_index = None
    for idx, directive in enumerate(server_block.get("block", [])):
        if directive.get("directive") == "location":
            args = directive.get("args", [])
            if args and args[0] == "/":
                location_index = idx
                break

    # Build the new location block for /prerenderio
    location_prerenderio = {
        "directive": "location",
        "args": ["/prerenderio"],
        "block": [
            {
                "directive": "if",
                "args": ["$prerender", "=", "0"],
                "block": [
                    {"directive": "return", "args": ["404"]}
                ]
            },
            {"directive": "proxy_set_header", "args": ["X-Prerender-Token", "YOUR_TOKEN"]},
            {"directive": "proxy_set_header", "args": ["X-Prerender-Int-Type", "Nginx_Rev_Proxy"]},
            {"directive": "proxy_hide_header", "args": ["Cache-Control"]},
            {"directive": "add_header", "args": ["Cache-Control", "private,max-age=600,must-revalidate"]},
            {"directive": "resolver", "args": ["8.8.8.8", "8.8.4.4"]},
            {"directive": "set", "args": ["$prerender_host", "service.prerender.io"]},
            {"directive": "proxy_pass", "args": ["https://$prerender_host"]},
            {"directive": "rewrite", "args": [".*", "/$scheme://$host$request_uri?", "break"]}
        ]
    }

    if location_index is not None:
        server_block.setdefault("block", []).insert(location_index + 1, location_prerenderio)
    else:
        server_block.setdefault("block", []).append(location_prerenderio)
