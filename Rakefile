
require "nokogiri"

desc "Create a new draft"
task :draft do
  meta = get_metadata(:title, :slug, :categories)
  path = File.join('_drafts', "#{meta[:slug]}.md")
  text = <<~EOF
    ---
    layout: post
    title: "#{meta[:title]}"
    date: #{Time.now.strftime('%Y-%m-%d')}
    categories:
      #{meta[:categories].split(", ").map{"- #{_1}"}.join("\n  ")}
    ---
  EOF
  File.open(path, 'w') { |f| f << text }
end

desc "Publish a draft"
task :publish do
  draft_files = Dir.glob('_drafts/*.md')
  draft_file = IO.popen(['fzf', '--prompt=Select a draft to publish: ', '--layout=reverse', '--height=40%'], 'r+') do |fzf|
    fzf.puts draft_files
    fzf.close_write
    fzf.gets&.strip
  end

  next if draft_file.empty?

  filename = File.basename(draft_file)
  new_filename = "#{Time.now.strftime('%Y-%m-%d')}-#{filename}"
  new_path = File.join('_posts', new_filename)

  content = File.read(draft_file)
    .sub(/^date: .+$/, "date: #{Time.now.strftime('%Y-%m-%d')}")

  File.open(draft_file, 'w') { |f| f << content }
  File.rename(draft_file, new_path)
  puts "Draft published as #{new_path}"
end

desc "Unpublish a post"
task :unpublish do
  committed_files = `git ls-files _posts/*.md`.split("\n")
  post_files = Dir.glob('_posts/*.md') - committed_files
  post_file = IO.popen(['fzf', '--prompt=Select a post to unpublish: ', '--layout=reverse', '--height=40%'], 'r+') do |fzf|
    fzf.puts post_files
    fzf.close_write
    fzf.gets&.strip
  end

  next if post_file.empty?

  filename = File.basename(post_file)
  new_filename = filename.sub(/^\d{4}-\d{2}-\d{2}-/, '')
  new_path = File.join('_drafts', new_filename)

  File.rename(post_file, new_path)
  puts "Post unpublished as #{new_path}"
end

desc "Create a new post"
task :post do
  meta = get_metadata(:title, :slug, :categories)
  filename = "#{Time.now.strftime '%Y-%m-%d'}-#{meta[:slug]}.md"
  path = File.join('_posts', filename)
  text = <<~EOF
    ---
    layout: post
    title: "#{meta[:title]}"
    date: #{Time.now.strftime('%Y-%m-%d')}
    categories: #{meta[:categories].downcase}
    ---
  EOF
  File.open(path, 'w') { |f| f << text }
end

desc "Create a new page"
task :page do
  meta = get_metadata(:title, :slug)
  path = File.join('.', "#{meta[:slug]}.md")
  text = <<~EOF
    ---
    layout: page
    title: "#{meta[:title]}"
    date: #{Time.now.strftime('%Y-%m-%d')}
    ---
  EOF
  File.open(path, 'w') { |f| f << text }
end

desc "Print stats about this blog"
task :stats do
  yearly_stats = Dir["_posts/*"]
    .map { |filepath| filepath.delete_prefix("_posts/").split("-").first }
    .tally
    .sort_by { |k, _v| k }
    .to_h

  total_posts = yearly_stats.values.sum(&:to_i)

  total_words = Dir["_site/posts/*/index.html"]
    .sum(&method(:word_count))

  puts <<~STATS
    Total posts: #{total_posts.to_s.rjust(8)}
    Total words: #{number_to_human(total_words).rjust(8)}

    Yearly stats

  STATS

  yearly_stats.each do |year, count|
    puts "#{year}\t#{count.to_s.rjust(4)}\t#{"|" * count}"
  end
end

def get_metadata(*keys)
  meta = {}
  keys.each { |k| meta[k] = ask("#{k.capitalize}: ") }
  meta
end

def ask(qn)
  STDOUT.print qn
  STDIN.gets.chomp
end

def word_count(file)
  File.open(file) { |f| Nokogiri::HTML(f) }
    .at_css(".post .content")
    .text
    .strip
    .split
    .count
end

def number_to_human(n)
  n.to_s
    .chars
    .reverse
    .each_slice(3)
    .map(&:join)
    .join(",")
    .reverse
end
