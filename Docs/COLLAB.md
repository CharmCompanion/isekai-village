# Collaborate on another PC

Both machines need the **same Unreal Engine 5.8** build (Epic Launcher → Unreal Engine → 5.8).

## 1. Install tools
- [Git](https://git-scm.com/download/win)
- [Git LFS](https://git-lfs.com/) then run `git lfs install` once
- Visual Studio 2022 with **Game development with C++** (for compiling the game module)

## 2. Get the project
Clone this repo. Do **not** copy `Binaries/`, `Intermediate/`, or `Saved/` from the other PC.

## 3. Restore Fab / marketplace packs
Those folders are gitignored (they are huge and re-downloadable). Copy them from the other PC's `Content/` **or** reinstall from Fab. The ignore list is in `.gitignore` under `Content/`. Missing packs show as missing assets, not a failed open.

## 4. Open in Unreal
1. Double-click `IsekaiVillage.uproject`
2. If prompted, compile the `IsekaiVillage` module and let it rebuild
3. If Visual Studio files are missing: right-click the `.uproject` → **Generate Visual Studio project files**, then open again

## 5. Daily workflow
- One person should not have the same `.uasset` / `.umap` open for save on two PCs at once.
- Commit `Source/`, `Config/`, `Content/` (project maps/assets), `Scripts/`, `Docs/`.
- Never commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`.

Engine association is `"5.8"` in `IsekaiVillage.uproject`. A different engine version will ask to convert the project — do not convert unless you both switch together.
