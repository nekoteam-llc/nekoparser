function trim(str, ch) {
  var start = 0,
    end = str.length;

  while (start < end && str[start] === ch)
    ++start;

  while (end > start && str[end - 1] === ch)
    --end;

  return (start > 0 || end < str.length) ? str.substring(start, end) : str;
}

function buildURLRegex(urls) {
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
  let min_parts = 1000;
  for (let i = 0; i < urls.length; i++) {
    parts = trim(urls[i], "/").split("/").length;
    if (parts < min_parts) {
      min_parts = parts;
    }
  }

  min_parts -= common_parts.length;

  for (let i = 0; i < common_parts.length; i++) {
    url_string += `\\/${common_parts[i].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`;
  }

  url_string = url_string.substring(2);
  for (let i = 0; i < min_parts; i++) {
    url_string += `\\/[^/]+?`;
  }
  url_string += "\\/?(?:[?#].+?)?$";
  offset = url_string.lastIndexOf("[^/]+?");
  url_string = url_string.substring(0, offset) + url_string.substring(offset).replace("[^/]+?", "[^/]+");
  return url_string;
}

function highlightSimilar(link) {
  if (document.querySelector(".swp-new-button") !== null) {
    document.querySelector(".swp-new-button").remove();
  }
  url = link.href;
  const path_component = url.startsWith("/")
    ? url.split("/")[1]
    : url.split("/")[3];
  current_elem = link.parentNode;
  document.querySelectorAll(".swp-new-highlighted").forEach((elem) => {
    elem.classList.remove("swp-new-highlighted");
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
          current_links[i].classList.add("swp-new-highlighted");
        }
      }
      document.body.insertAdjacentHTML(
        "beforeend",
        `<div class="swp-new-button">
          Confirm
        </div>`
      );

      document.querySelector(".swp-new-button").addEventListener("click", () => {
        window.productXPATHFound = true;
        urls = [];
        document.querySelectorAll(".swp-new-highlighted").forEach((elem) => {
          if (!urls.includes(elem.href)) {
            urls.push(elem.href);
          }
        });

        url_string = buildURLRegex(urls);
        console.log(`Regex for products: ${url_string}`);

        window.localStorage.setItem("product_regex", url_string);

        document.querySelector(".swp-new-button").remove();
        document.querySelector(
          ".swp-new-tooltip p"
        ).innerText = `Regex for products saved. Now try to go to the second page.`;
        window.localStorage.setItem("swp-new-state", "pagination");
        document.querySelector(".swp-new-highlighter").style.display = "block";

        document.querySelectorAll(".swp-new-highlighted").forEach((elem) => {
          elem.classList.remove("swp-new-highlighted");
        });
      });

      document.querySelector(
        ".swp-new-tooltip p"
      ).innerText = `If the products were highlighted correctly, click on the button in the top of the page. If not, open the product again.`;
      break;
    }
    current_elem = current_elem.parentNode;
  }
}

console.log("%cSWP Plugin is active 🎉", "color: #ff00ff; font-size: 22px;");
window.productXPATHFound = false;

function pause() {
  document.querySelector(".swp-new-highlighter").style.display = "none";
  document.querySelector(".swp-new-tooltip").style.display = "none";
}

function resume() {
  document.querySelector(".swp-new-highlighter").style.display = "block";
  document.querySelector(".swp-new-tooltip").style.display = "block";
}

document.addEventListener("keydown", (e) => {
  if (e.key === "p" || e.key == "з") {
    pause();
  }
})

document.addEventListener("keyup", (e) => {
  if (e.key === "p" || e.key == "з") {
    resume();
  }
})


function highlightElement(elem) {
  if (elem === null) return;
  const highlighter = document.querySelector(".swp-new-highlighter");
  if (elem.offsetWidth <= 0 || elem.offsetHeight <= 0) {
    return;
  }
  const rect = elem.getBoundingClientRect();
  highlighter.style.width = `${rect.width + 6}px`;
  highlighter.style.height = `${rect.height + 6}px`;
  highlighter.style.top = `${rect.top - 3}px`;
  highlighter.style.left = `${rect.left - 3}px`;
}

function injectTooltip() {
  document.body.insertAdjacentHTML(
    "beforeend",
    `<div class="swp-new-tooltip">
      <p></p>
    </div>`
  );

  setInterval(() => {
    const tooltip = document.querySelector(".swp-new-tooltip");
    tooltip.style.top = `${window.tooltipPositionY + 20}px`;
    tooltip.style.left = `${window.tooltipPositionX + 20}px`;
  }, 100);
}

function processHighlighter(e) {
  document.querySelector(".swp-new-highlighter").style.opacity = "1";

  window.tooltipPositionX = e.pageX;
  window.tooltipPositionY = e.pageY;

  const elems = document.elementsFromPoint(e.clientX, e.clientY);
  let elem = null;
  for (let i = 0; i < elems.length; i++) {
    if (elems[i].classList.contains("swp-new-highlighter")) {
      continue;
    }
    elem = elems[i];
    break;
  }
  highlightElement(elem);
}

function getXPath(element) {
  let selector = '';
  let foundRoot;
  let currentElement = element;
  do {
    const tagName = currentElement.tagName.toLowerCase();
    const parentElement = currentElement.parentElement;
    if (parentElement.childElementCount > 1) {
      const parentsChildren = [...parentElement.children];
      let tag = [];
      parentsChildren.forEach(child => {
        if (child.tagName.toLowerCase() === tagName) tag.push(child)
      })
      if (tag.length === 1) {
        selector = `/${tagName}${selector}`;
      } else {
        const position = tag.indexOf(currentElement) + 1;
        selector = `/${tagName}[${position}]${selector}`;
      }

    } else {
      selector = `/${tagName}${selector}`;
    }

    currentElement = parentElement;
    foundRoot = parentElement.tagName.toLowerCase() === 'html';
    if (foundRoot) selector = `/html${selector}`;
  }
  while (foundRoot === false);
  return selector;
}

function injectHighlighter() {
  document.body.insertAdjacentHTML(
    "beforeend",
    `<div class="swp-new-highlighter"></div>`
  );

  document.querySelector(".swp-new-highlighter").addEventListener("click", (e) => {
    const elems = document.elementsFromPoint(e.clientX, e.clientY);
    let elem = null;
    for (let i = 0; i < elems.length; i++) {
      if (elems[i].classList.contains("swp-new-highlighter")) {
        continue;
      }
      elem = elems[i];
      break;
    }
    console.log(elem);
    if (window.localStorage.getItem("swp-new-state") === "product") {
      document.querySelector(".swp-new-highlighter").style.display = "none";
      if (elem.tagName !== "A") {
        elem = elem.closest("a");
      }
      if (elem === null) {
        return;
      }

      highlightSimilar(elem);
    } else if (window.localStorage.getItem("swp-new-state") === "pagination") {
      document.querySelector(".swp-new-highlighter").style.display = "none";
      if (elem.tagName !== "A") {
        elem = elem.closest("a");
      }
      if (elem === null) {
        return;
      }

      url = elem.href;
      offset = url.lastIndexOf("2");
      url = url.substring(0, offset) + url.substring(offset).replace("2", "%swp-new-pagination%");
      console.log(`Regex for pagination: ${url}`);
      window.localStorage.setItem("pagination_regex", url);

      document.querySelector(
        ".swp-new-tooltip p"
      ).innerHTML = `Regex for pagination saved. Please, open the product <u>with the discount</u>`;

      window.localStorage.setItem("swp-new-state", "product-page");
    } else if (window.localStorage.getItem("swp-new-state") === "product-page") {
      window.knownProperties.push({
        property: window.availableProperties[0].name,
        xpath: getXPath(elem),
      });
      window.availableProperties.shift();
      if (window.availableProperties.length === 0) {
        document.querySelector(".swp-new-highlighter").style.display = "none";
        document.querySelector(
          ".swp-new-tooltip p"
        ).innerText = `All properties were selected. Redirecting back to the main page...`;
        fetch(`https://nekoparser.dan.tatar/api/v1/connector/sources/${window.sourceId}`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            xpaths: window.knownProperties,
            regexes: {
              product: window.localStorage.getItem("product_regex"),
              pagination: window.localStorage.getItem("pagination_regex"),
            }
          }),
        }).then((response) => {
          if (response.status === 200) {
            window.location.href = "https://nekoparser.dan.tatar";
          } else {
            document.querySelector(
              ".swp-new-tooltip p"
            ).innerText = `Error while saving the properties. Try again.`;
          }
        });
      }
      selectProperty(window.availableProperties[0].name, window.availableProperties[0].description);
    }
  });

  document.addEventListener("scroll", () => {
    document.querySelector(".swp-new-highlighter").style.opacity = "0";
  });

  document.addEventListener("mousemove", (e) => {
    processHighlighter(e);
  });
}

function injectStyles() {
  document.head.insertAdjacentHTML(
    "beforeend",
    `<style>
      @import url("https://fonts.googleapis.com/css2?family=Hubballi&display=swap");
      a.swp-new-highlighted {
        background: rgba(50, 0, 0, 0.1);
        border: 1px solid rgba(50, 0, 0, 0.3);
        border-radius: 5px;
      }

      .swp-new-tooltip {
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

      .swp-new-tooltip p {
        margin: 0;
        color: #f2f2f2;
      }

      .swp-new-button {
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

      .swp-new-highlighter {
        position: fixed;
        top: 0;
        left: 0;
        background: rgba(50, 0, 0, 0.1);
        border: 1px solid rgba(50, 0, 0, 0.3);
        border-radius: 5px;
        transition: all .05s linear;
        z-index: 9999;
      }
    </style>`
  );
}

function initOnMainPage() {
  injectTooltip();
  injectStyles();

  document.querySelector(".swp-new-tooltip p").innerText = `Open any product.`;
  window.localStorage.setItem("swp-new-state", "product");

  injectHighlighter();
}

function selectProperty(property, description) {
  document.querySelector(".swp-new-tooltip p").innerHTML = `Select the <u>${description}</u>.`;
}

function initOnProductPage() {
  injectTooltip();
  injectStyles();
  injectHighlighter();

  getAvailableProperties().then((properties) => {
    window.availableProperties = properties;
    window.knownProperties = [];
    selectProperty(properties[0].name, properties[0].description);
  });
}

function checkIfOnMainPage() {
  if (!window.localStorage.getItem("product_regex"))
    return;

  const regex = new RegExp(window.localStorage.getItem("product_regex"));
  console.log(regex);
  if (!regex.test(window.location.href)) {
    window.localStorage.setItem("swp-new-state", "product");
    initOnMainPage();
  }
}

function initPluginVerified() {
  if (window.localStorage.getItem("swp-new-state") !== "product-page") {
    initOnMainPage();
    return
  }

  checkIfOnMainPage();
  initOnProductPage();
}

function initPlugin() {
  fetch("https://nekoparser.dan.tatar/api/v1/connector/sources", {
    credentials: "include",
  }).then((response) => {
    response.json().then((data) => {
      const sources = data.sources;
      const currentDomain = window.location.hostname;
      for (let i = 0; i < sources.length; i++) {
        const source = sources[i];
        if (source.domain === currentDomain) {
          window.sourceId = source.id;
          initPluginVerified();
        }
      }
    });
  })
}

function getAvailableProperties() {
  return new Promise((resolve, reject) => {
    fetch("https://nekoparser.dan.tatar/api/v1/connector/properties", {
      credentials: "include",
    }).then((response) => {
      response.json().then((data) => {
        const properties = data.properties;
        resolve(properties);
      });
    });
  });
}

window.addEventListener("load", () => {
  initPlugin();
});
