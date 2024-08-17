source "https://rubygems.org"

# core installations
gem "json"
gem "webrick"
gem "github-pages", group: :jekyll_plugins

# additional plugins
group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-sitemap"
  gem "jekyll-seo-tag"
end

# "Windows and JRuby does not include zoneinfo files, so bundle the tzinfo-data 
#  gem and associated library." -- Jekyll
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", :platforms => [:mingw, :x64_mingw, :mswin]
