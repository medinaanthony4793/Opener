# Best Practices

## Extracting from HTML

The following formats return `null` in a timely manner if the regex isn't matched. Replace `YOUR_REGEX_HERE`.

`script` field:

```javascript
function process(url, completionHandler) { var xmlhttp = new XMLHttpRequest(); xmlhttp.onreadystatechange = function() { if (xmlhttp.readyState == 4 && xmlhttp.status == 200) { var res = xmlhttp.responseText; var results = RegExp('.*(YOUR_REGEX_HERE).*').exec(res); var match = results != null && results.length > 1 ? results[1] : null; completionHandler(match); } }; xmlhttp.open('GET', url, true); xmlhttp.send(); }
```

`script2` field:

```javascript
function process(url, completionHandler) { var res = httpRequest(url); var results = RegExp('.*(YOUR_REGEX_HERE).*').exec(res); var match = results != null && results.length > 1 ? results[1] : null; completionHandler(match); }
```

## URL Encoding

Replace `YOUR_*_HERE`.

`script` and `script2` fields:

```javascript
function process(url, completionHandler) { completionHandler('YOUR_SCHEME_HERE://YOUR_PATH_HERE?url=' + encodeURIComponent(url)); }
```
