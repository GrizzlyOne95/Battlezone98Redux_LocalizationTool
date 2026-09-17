# SignPath Foundation setup

The repository is prepared for SignPath Foundation Authenticode signing, but signing remains disabled until the SignPath project has been approved and the repository variables/secrets below are configured.

## SignPath project

Use the following application identity when creating the SignPath project:

- Project / product name: `Battlezone Localization Tool`
- Windows executable: `BZLocalizationTool.exe`
- Source repository: `https://github.com/GrizzlyOne95/Battlezone98Redux_LocalizationTool`
- Trusted build system: GitHub.com
- Signing policy: release signing with manual approval

Install the SignPath GitHub App for this repository and link the SignPath project to the GitHub.com trusted build system so origin verification can validate GitHub Actions builds.

The GitHub Actions artifact submitted to SignPath is a ZIP produced by `actions/upload-artifact`; configure the SignPath artifact configuration to locate and Authenticode-sign `BZLocalizationTool.exe` inside that artifact. Enforce Windows file metadata for the product name `Battlezone Localization Tool` and a consistent product/file version.

## GitHub repository configuration

After SignPath approval, create these repository **Variables**:

- `SIGNPATH_ORGANIZATION_ID`
- `SIGNPATH_PROJECT_SLUG`
- `SIGNPATH_SIGNING_POLICY_SLUG`
- `SIGNPATH_ENABLED` = `true`

Create this repository **Secret**:

- `SIGNPATH_API_TOKEN`

Keep `SIGNPATH_ENABLED` unset or set to `false` until all other values are valid. With signing disabled, the workflow continues to produce unsigned Windows builds as before.

## Release behavior

For a version tag such as `v2.2`, the workflow will:

1. Build `BZLocalizationTool.exe` on a GitHub-hosted Windows runner.
2. Generate consistent Windows version metadata from the tag.
3. Upload the unsigned executable as a GitHub Actions artifact.
4. Submit that artifact to SignPath using the official GitHub action.
5. Wait for the required signing approval and completion.
6. Upload the signed `BZLocalizationTool.exe` as the Windows release artifact.
7. Publish the GitHub Release only after the build/signing job succeeds.

Manual `workflow_dispatch` builds remain unsigned; SignPath signing is intentionally restricted to version-tagged releases.

## Eligibility check

The project itself is MIT licensed. `BZONE.ttf` is a fan-made font authored by **ScrapPool**, inspired by the Battlezone visual style, and was provided by its author for free use. It is not an extracted game font. That provenance is documented in `THIRD_PARTY_NOTICES.md`.

SignPath Foundation currently requires an OSI-approved open-source license for all bundled components. "Free use" permission is useful provenance, but it is not automatically the same thing as an OSI-approved license. Before submitting the Foundation application, obtain or document an explicit open-source license grant from ScrapPool for `BZONE.ttf` (for example, SIL Open Font License 1.1 if the author agrees), then add the corresponding license text to the repository.

The repository README contains the required **Code signing policy**, including team roles and privacy/network-transfer disclosure.
