const repository =
    "ariyabrave/FatePlanner";

const apiUrl =
    `https://api.github.com/repos/${repository}/releases/latest`;

const fallbackRelease =
    `https://github.com/${repository}/releases/latest`;


function findAsset(
    assets,
    matcher
) {
    return assets.find(
        (asset) =>
            matcher.test(asset.name)
    );
}


async function loadLatestRelease() {
    try {
        const response =
            await fetch(
                apiUrl,
                {
                    headers: {
                        Accept:
                            "application/vnd.github+json"
                    }
                }
            );

        if (!response.ok) {
            throw new Error(
                `GitHub API returned ${response.status}`
            );
        }

        const release =
            await response.json();

        const version =
            release.tag_name;

        const assets =
            release.assets || [];

        document
            .getElementById(
                "latest-version"
            )
            .textContent =
                `Latest ${version}`;


        const windowsSetup =
            findAsset(
                assets,
                /^FatePlanner-Windows-Setup-v.*\.exe$/
            );

        const windowsPortable =
            findAsset(
                assets,
                /^FatePlanner-Windows-Portable-v.*\.zip$/
            );

        const linuxBuild =
            findAsset(
                assets,
                /^FatePlanner-Linux-x86_64-v.*\.tar\.gz$/
            );

        const checksums =
            findAsset(
                assets,
                /^SHA256SUMS\.txt$/
            );


        if (windowsSetup) {
            document
                .getElementById(
                    "windows-download"
                )
                .href =
                    windowsSetup
                        .browser_download_url;

            document
                .getElementById(
                    "windows-setup-download"
                )
                .href =
                    windowsSetup
                        .browser_download_url;
        }


        if (windowsPortable) {
            document
                .getElementById(
                    "windows-portable-download"
                )
                .href =
                    windowsPortable
                        .browser_download_url;
        }


        if (linuxBuild) {
            document
                .getElementById(
                    "linux-download"
                )
                .href =
                    linuxBuild
                        .browser_download_url;

            document
                .getElementById(
                    "linux-package-download"
                )
                .href =
                    linuxBuild
                        .browser_download_url;
        }


        if (checksums) {
            document
                .getElementById(
                    "checksums-download"
                )
                .href =
                    checksums
                        .browser_download_url;
        }


        document
            .getElementById(
                "release-page"
            )
            .href =
                release.html_url ||
                fallbackRelease;

    } catch (error) {
        console.warn(
            "Could not load latest FatePlanner release:",
            error
        );

        document
            .getElementById(
                "latest-version"
            )
            .textContent =
                "Latest release";
    }
}


loadLatestRelease();