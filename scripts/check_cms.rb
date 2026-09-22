# Run with: bundle exec ruby scripts/check_cms.rb
# Fixtures and generated output stay in a temporary copy of the site.
require 'jekyll'
require 'tmpdir'
require 'fileutils'
require 'yaml'
require 'date'

ROOT = File.expand_path('..', __dir__)
def check(condition, message)
  raise message unless condition
end

cms = YAML.load_file(File.join(ROOT, '.pages.yml'))
check(cms.fetch('media') == { 'input' => 'images', 'output' => '/images' }, 'Media paths changed')
check(cms.fetch('content').map { |c| c['path'] }.sort == %w[_news _posts _videogames], 'Missing collection')
cms.fetch('content').each do |collection|
  fields = collection.fetch('fields')
  check(fields.find { |f| f['name'] == 'published' }.fetch('default') == false, 'New entries must be drafts')
  %w[title date].each { |key| check(fields.find { |f| f['name'] == key }['required'], "Missing required #{key}") }
end
categories = Dir[File.join(ROOT, 'categories', '*.md')].map { |f| File.read(f)[/^category: (.+)$/, 1] }.sort
options = cms['content'].find { |c| c['name'] == 'posts' }['fields'].find { |f| f['name'] == 'categories' }['options']
check(options['values'].sort == categories, 'Category choices do not match category pages')

ENV['JEKYLL_ENV'] = 'production'
Dir.mktmpdir('hilmybaja-cms-') do |tmp|
  source = File.join(tmp, 'source')
  destination = File.join(tmp, 'output')
  FileUtils.mkdir_p(source)
  Dir.children(ROOT).reject { |name| %w[.git .venv _site .jekyll-cache .bundle vendor].include?(name) }.each do |name|
    FileUtils.cp_r(File.join(ROOT, name), source)
  end
  config = Jekyll.configuration('source' => source, 'destination' => destination, 'quiet' => true)
  build = -> { site = Jekyll::Site.new(config); site.process; site }
  baseline = build.call
  existing = (baseline.posts.docs + baseline.collections['videogames'].docs).map { |doc| [doc.relative_path, doc.url] }.to_h
  check(baseline.posts.docs.any? { |doc| doc.path.end_with?('.markdown') }, 'Legacy Markdown post missing')
  check(!baseline.posts.docs.any? { |doc| doc.data['title'] == 'Smoothies' }, 'Smoothies draft was published')
  caption_post = File.read(File.join(destination, 'posts', 'dies-natalis', 'index.html'))
  check(caption_post.include?('<sub>Photo courtesy of Guy Ackermans</sub>'), 'HTML caption changed')
  check(caption_post.include?('/images/posts/dies.jpg'), 'Existing image path changed')
  fixtures = {
    '_news' => { 'excerpt' => 'CMS_NEWS_SENTINEL [link](https://example.com)', 'image' => '/images/hilmy.jpg' },
    '_posts' => { 'categories' => 'personal' },
    '_videogames' => { 'platforms' => 'PC', 'genres' => 'RPG', 'excerpt' => 'CMS_GAME_SENTINEL', 'images' => ['/images/hilmy.jpg'] }
  }
  [false, true, false].each do |published|
    fixtures.each do |folder, extra|
      data = { 'title' => "CMS #{folder} sentinel", 'date' => '2020-01-02', 'published' => published }.merge(extra)
      File.write(File.join(source, folder, '2024-01-01-cms-sentinel.md'), data.to_yaml + "---\n\nCMS_BODY_SENTINEL\n")
    end
    site = build.call
    homepage = File.read(File.join(destination, 'index.html'))
    games = File.read(File.join(destination, 'videogames', 'index.html'))
    check(homepage.include?('CMS_NEWS_SENTINEL') == published, 'News visibility incorrect')
    check(games.include?('CMS_GAME_SENTINEL') == published, 'Game visibility incorrect')
    check(File.exist?(File.join(destination, 'posts', 'cms-sentinel', 'index.html')) == published, 'Post output visibility incorrect')
    check(File.exist?(File.join(destination, 'videogames', 'cms-sentinel', 'index.html')) == published, 'Game output visibility incorrect')
    if published
      post = site.posts.docs.find { |doc| doc.data['title'] == 'CMS _posts sentinel' }
      check(post.data['layout'] == 'post', 'Default post layout missing')
      check(post.date.year == 2020, 'Backdated front matter ignored')
      check(homepage.include?('02 Jan'), 'Backdated display missing')
      check(games.include?('/images/hilmy.jpg'), 'New screenshot path missing')
      check(File.read(File.join(destination, 'categories', 'personal', 'index.html')).include?('cms-sentinel'), 'Published category entry missing')
      %w[feed.xml sitemap.xml].each do |file|
        check(File.read(File.join(destination, file)).include?('/posts/cms-sentinel/'), "Published URL missing from #{file}")
      end
    else
      Dir[File.join(destination, '**', '*')].select { |f| File.file?(f) && %w[.html .xml].include?(File.extname(f)) }.each do |file|
        check(!File.read(file).match?(/CMS_(?:BODY|NEWS|GAME)_SENTINEL|cms-sentinel/), "Draft leaked into #{file}")
      end
    end
    existing.each do |path, url|
      doc = (site.posts.docs + site.collections['videogames'].docs).find { |d| d.relative_path == path }
      check(doc && doc.url == url, "Existing URL changed: #{path}")
    end
  end
end
puts 'CMS configuration and production draft/publish/unpublish checks passed.'
