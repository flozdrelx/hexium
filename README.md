# Hexium Browser Prototype V0.04-unstable

#### Experimental mini browser project

A CLI-based browser prototype currently in active development.

---

# Current Features

* CLI interface
* Website downloading support
* Export downloaded websites as:
  * Markdown (`.md`)
  * HTML (`.html`)
  * Both formats simultaneously
* Optional asset downloading when saving HTML:
  * CSS files
  * Images
  * Scripts and common media references
* Socket support (only HTTP)
* Additional networking commands
* Individual folders for downloaded websites to avoid asset conflicts
* HTTPS support
* SSL, requests are safe
* Redirect handling for HTTP requests and website downloads

---

# Planned Features

* Basic DOM support and browsing history (V0.05)
* Improved commands and download manager (V0.06)
* Better HTML parser (V0.07)
* GUI support (V0.08 or V0.1)
* Basic HTML rendering

---

# Websites Folder

Downloaded websites are stored in:

```text
Scripts/websites
```

Each downloaded site is saved in its own folder:

```text
Scripts/websites/Example_Domain/index.html
Scripts/websites/Example_Domain/index.md
Scripts/websites/Example_Domain/assets/
```

Example commands (for downloading):

```text
get example.com
get example.com html --assets
get example.com both
```

---

# Current Status

The prototype is currently being tested for the next version.
