const highlight_similar = (link) => {
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
        window.productXrefs = [];
        document.querySelectorAll(".swp-highlighted").forEach((elem) => {
          if (!window.productXrefs.includes(elem.href)) {
            window.productXrefs.push(elem.href);
          }
        });
        document.querySelector(".swp-button").remove();
        document.querySelector(
          ".swp-tooltip p"
        ).innerText = `XREF for products saved. Now try to open the second page of the website.`;
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
};

const hook_event_listeners = () => {
  document.querySelectorAll("a").forEach((link) => {
    link.removeEventListener("click", () => {});
  });
  document.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      console.log(link.href);
      if (!window.productXrefFound) {
        highlight_similar(link);
      } else {
        window.paginationXrefFound = true;
        document.querySelector(
          ".swp-tooltip p"
        ).innerText = `XREF for pagination saved. Redirecting to product page...`;
        window.location.href = window.productXrefs[0];
      }
    });
  });
};

console.log("Hook'er is active!");
window.productXrefFound = false;

setInterval(() => {
  hook_event_listeners();
}, 1500);

window.addEventListener("load", () => {
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
    tooltip.style.top = window.tooltipPositionY + 20 + "px";
    tooltip.style.left = window.tooltipPositionX + 20 + "px";
  }, 100);

  document.addEventListener("mousemove", (e) => {
    window.tooltipPositionX = e.pageX;
    window.tooltipPositionY = e.pageY;
  });
});
