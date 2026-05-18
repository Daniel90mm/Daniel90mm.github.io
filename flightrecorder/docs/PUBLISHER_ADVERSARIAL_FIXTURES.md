# Publisher adversarial fixture inventory

Categories of adversarial inputs needed before any curator/reviewer redaction
code is written. The publisher auto-publishes on a 24h delay with no human
approval - tests must prove the redaction pipeline catches these.

## Fixture categories

### 1. Real-looking names
Fake but realistic full names in various formats:
- `"Mikkel Jensen"` (Danish first+last)
- `"Dr. Anna Svensson"` (title + name)
- `names embedded in conversation` (casual first-name references)

### 2. Email addresses
- `mikkel.jensen@dtu.dk`
- `anna.svensson@gmail.com`
- `user@private-repo.internal`

### 3. Repo URLs
- `github.com/anomalyco/private-project`
- `gitlab.internal.corp/team/secret-tool`
- `bitbucket.org/personal/private-repo`

### 4. Course codes with semesters
- `"02100 Algorithms and Data Structures, spring 2026"`
- `"34540 Photonics, fall 2025"`
- `"DTU course 02510 spring 2026"`

### 5. Sensitive personal content
- Medical: `"diagnosed with..."`
- Financial: `"cost me 45000 kr..."`
- Relationships: `"my partner works at..."`
- Location: `"my address is Strandvejen 42..."`

### 6. Mixed benign/doxxing
Longer text samples where benign content surrounds a single piece of sensitive
information, testing that the curator/reviewer pipeline isolates and redacts
without damaging the benign portion.

## Expected behavior

- Curator redacts doxxing content from named categories.
- Reviewer (different provider) catches what the curator missed.
- After both passes, the output contains zero identifiable real names (except
  `daniel`), emails, URLs, course codes with semesters, or sensitive personal
  content.
