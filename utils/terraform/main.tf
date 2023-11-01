# Mangement of the GitHub project.

resource "github_repository" "varfish-cli" {
  name         = "varfish-cli"
  description  = "VarFish REST API client (CLI + Python package)"
  homepage_url = "https://github.com/bihealth/varfish-cli"
  visibility   = "public"
  topics = [
    "bioinformatics",
    "genetics",
    "varfish",
    "vcf",
  ]

  has_issues      = true
  has_downloads   = true
  has_discussions = false
  has_projects    = false

  allow_auto_merge   = true
  allow_rebase_merge = false
  allow_merge_commit = false

  delete_branch_on_merge = true

  vulnerability_alerts = true

  squash_merge_commit_message = "BLANK"
  squash_merge_commit_title   = "PR_TITLE"
}
