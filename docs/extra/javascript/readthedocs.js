/*
This snippet adds support for the readthedocs version selector
https://docs.readthedocs.io/en/stable/intro/mkdocs.html#integrate-the-read-the-docs-version-menu-into-your-site-navigation

*/
document.addEventListener(
    "readthedocs-addons-data-ready",
    function (event) {
        // Early exit if the item already exists - preventing duplicate version menus
        if (document.querySelector(".md-version")) {
            return;
        }

        const config = event.detail.data();
        const versioning = `
<div class="md-version">
<button class="md-version__current" aria-label="Select version">
${config.versions.current.slug}
</button>

<ul class="md-version__list">
${config.versions.active.map(
            (version) => `
<li class="md-version__item">
<a href="${version.urls.documentation}" class="md-version__link">
    ${version.slug}
</a>
        </li>`).join("\n")}
</ul>
</div>`;

        document.querySelector(".md-header__topic").insertAdjacentHTML("beforeend", versioning);
    });
