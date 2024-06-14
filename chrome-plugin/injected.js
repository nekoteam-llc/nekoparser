function build_url_regex(urls) {
  common_parts = [];
  base_parts = urls[0].split("/");
  for (let i = 0; i < base_parts.length; i++) {
    common = true;
    for (let j = 1; j < urls.length; j++) {
      if (urls[j].split("/")[i] !== base_parts[i]) {
        common = false;
        break;
      }
    }
    if (common) {
      common_parts.push(base_parts[i]);
    } else {
      break;
    }
  }
  url_string = "";
  for (let i = 0; i < common_parts.length; i++) {
    url_string += `\\/${common_parts[i].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`;
  }
  url_string = url_string.substring(2);
  for (let i = common_parts.length; i < base_parts.length; i++) {
    if (base_parts[i] === "") {
      continue;
    }
    url_string += `\\/[^/]*?`;
  }
  url_string += "\\/?(?:[?#].*?)?$";
  offset = url_string.lastIndexOf("[^/]*?");
  url_string = url_string.substring(0, offset) + url_string.substring(offset).replace("[^/]*?", "[^/]*");
  return url_string;
}


function highlight_similar(link) {
  url = link.href;
  const path_component = url.startsWith("/")
    ? url.split("/")[1]
    : url.split("/")[3];
  current_elem = link.parentNode;
  document.querySelectorAll(".swp-highlighted").forEach((elem) => {
    elem.classList.remove("swp-highlighted");
  });
  while (true) {
    if (current_elem.tagName === "BODY") {
      break;
    }
    current_links = current_elem.querySelectorAll("a");
    current_similar = 0;
    for (let i = 0; i < current_links.length; i++) {
      if (current_links[i].href.includes(path_component)) {
        current_similar++;
      }
    }
    if (current_similar >= 10) {
      for (let i = 0; i < current_links.length; i++) {
        if (current_links[i].href.includes(path_component)) {
          current_links[i].classList.add("swp-highlighted");
        }
      }
      document.body.insertAdjacentHTML(
        "beforeend",
        `<div class="swp-button">
          Confirm
        </div>`
      );

      document.querySelector(".swp-button").addEventListener("click", () => {
        window.productXrefFound = true;
        urls = [];
        document.querySelectorAll(".swp-highlighted").forEach((elem) => {
          if (!urls.includes(elem.href)) {
            urls.push(elem.href);
          }
          window.sampleProductUrl = elem.href;
        });

        url_string = build_url_regex(urls);
        console.log(`Regex for products: ${url_string}`);

        window.localStorage.setItem("product_regex", url_string);

        document.querySelector(".swp-button").remove();
        document.querySelector(
          ".swp-tooltip p"
        ).innerText = `Regex for products saved. Now try to open the second page of the website.`;
        document.querySelectorAll(".swp-highlighted").forEach((elem) => {
          elem.classList.remove("swp-highlighted");
        });
      });

      document.querySelector(
        ".swp-tooltip p"
      ).innerText = `If the products were highlighted correctly, click on the button in the top of the page. If not, open the product again.`;
      break;
    }
    current_elem = current_elem.parentNode;
  }
}

function hook_event_listeners() {
  document.querySelectorAll("a").forEach((link) => {
    link.removeEventListener("click", () => { });
  });
  document.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      console.log(link.href);
      if (!window.productXrefFound) {
        highlight_similar(link);
      } else {
        url = link.href;
        offset = url.lastIndexOf("2");
        url = url.substring(0, offset) + url.substring(offset).replace("2", "[0-9]+");
        console.log(`Regex for pagination: ${url}`);
        window.localStorage.setItem("pagination_regex", url);

        document.querySelector(
          ".swp-tooltip p"
        ).innerText = `Regex for pagination saved. Redirecting to product page...`;
        window.location.href = window.sampleProductUrl;
      }
    });
  });
}

console.log("Hook'er is active!");
window.productXrefFound = false;

window.addEventListener("load", () => {
  if (window.localStorage.getItem("product_regex")) {
    console.log(window.localStorage.getItem("product_regex"), window.localStorage.getItem("pagination_regex"));
    return;
  }

  setInterval(() => {
    hook_event_listeners();
  }, 1500);

  document.body.insertAdjacentHTML(
    "beforeend",
    `<div class="swp-tooltip">
      <p>Please, <span style="color: #f2f2f2">open any product</span></p>
    </div>`
  );

  document.head.insertAdjacentHTML(
    "beforeend",
    `<style>
      @import url("https://fonts.googleapis.com/css2?family=Hubballi&display=swap");
      a.swp-highlighted {
        border: 2px solid red;
        border-radius: 5px;
      }

      .swp-tooltip {
        width: fit-content;
        height: fit-content;
        background: #111;
        color: white;
        font-family: "Hubballi", sans-serif;
        position: absolute;
        top: 0;
        left: 0;
        padding: 10px 20px;
        border-radius: 15px;
        transition: all 0.1s ease-in;
        z-index: 1000;
      }

      .swp-tooltip p {
        margin: 0;
        color: #f2f2f2;
      }

      .swp-button {
        position: fixed;
        top: 0;
        left: 0;
        background: #111;
        color: white;
        padding: 10px 20px;
        border-radius: 15px;
        font-family: "Hubballi", sans-serif;
        cursor: pointer;
        transition: all 0.1s ease-in;
        z-index: 1000;
      }
    </style>`
  );

  setInterval(() => {
    const tooltip = document.querySelector(".swp-tooltip");
    tooltip.style.top = `${window.tooltipPositionY + 20}px`;
    tooltip.style.left = `${window.tooltipPositionX + 20}px`;
  }, 100);

  document.addEventListener("mousemove", (e) => {
    window.tooltipPositionX = e.pageX;
    window.tooltipPositionY = e.pageY;
  });
});
