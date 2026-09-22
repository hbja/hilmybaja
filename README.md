
# hilmybaja.com

This repository contains the Jekyll theme and content of my blog.

### Editing with Pages CMS

1. After the CMS changes reach GitHub, open [Pages CMS](https://app.pagescms.org), sign in with GitHub, and install its GitHub App with access to **hbja/hilmybaja** only.
2. First select a temporary branch containing these changes (for example, `cms-check`). Create a News draft, reopen it to check Published is off, and try an image upload. Check an existing published entry too. This branch does not deploy the site.
3. For everyday editing select **master**, then **News**, **Blog Posts**, or **Videogames**. Fill in the title and date, write your text, and save. New entries start with **Published** off.
4. When ready, enable **Published** and save. To unpublish, turn it off and save again. Saving edits to an already published entry also updates the website.

Drafts and uploaded images are still public in this GitHub repository; the toggle only hides entries from the website. Keep confidential writing elsewhere. There is no full-site draft preview or scheduled publishing. Use a current or past blog date: future-dated posts wait for a build after that date, and there is no scheduled build to publish them automatically.

Use the image picker or the formatted editor's image button to upload into `images`. New image links start with `/images/`; existing files and links do not need moving. Screenshots can be added and reordered in a videogame's image list. Avoid overwriting images used by other entries. Uploaded files are not removed when an entry is unpublished.

News text is saved in the existing `excerpt` field. Blog and game text is saved as Markdown beneath the front matter. The **Source** switch is available for special Markdown or HTML such as photo captions; inspect these after editing. Categories use the existing category pages; adding a new category requires a repository change.

Filenames are generated from the creation date and title. Keep an existing filename when editing to preserve its URL. The date field controls the displayed date, including a game's completion date; it can differ from the filename date.

After saving on master, check [Deploy Jekyll site to Pages](https://github.com/hbja/hilmybaja/actions/workflows/jekyll.yml). Once the run succeeds, refresh [the website](https://hilmybaja.com). A failed build leaves the previous deployment live; open the failed run for details. During first rollout, verify one genuine News update triggers this workflow, then check the blog and videogame editors. Do not publish test entries on master.

To recover an accidental edit, use the file's GitHub history to find the previous content and restore it with a new commit (or copy the previous text back into the CMS). Reverting a commit also triggers publishing. When working locally after CMS edits, pull the remote changes before pushing.

The editor configuration is `.pages.yml`; hosting and publishing still use Jekyll and GitHub Pages. No CMS credentials belong in this repository. The older Rake tasks below use a separate `_drafts` workflow; CMS drafts stay in their collection with `published: false`.

### Checking CMS publishing locally

With the locked dependencies installed, run `bundle exec ruby scripts/check_cms.rb`.
This checks the configuration and builds an isolated temporary copy through draft,
published, and unpublished states, including feeds, sitemap, category listings,
backdated posts, and removal of previously published pages. It does not publish
anything or modify your content. Hosted editor and upload checks still require
the GitHub App connection described above.

### Want to use this theme?

* Remove the existing content

```
$ rm -rf about notes _news/*.md slides _posts/*.md keybase.txt CNAME resume.html
```

* Edit the details from `_config.yml`.
  Make sure you leave the Google Analytics config blank
  if you don't use it.
* Change title in `index.html`

### Rake tasks

- `rake draft`:
  Creates a draft post in `_drafts`.
- `rake publish`:
  Prompts to pick a file from the `_drafts` folder,
  and publishes that to `_posts`.
- `rake unpublish`:
  Moves a file from `_posts` to `_drafts`.
