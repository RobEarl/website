#!/usr/bin/perl

use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use CGI qw(param);

use lib './lib';
use warnings;
use strict;

use Template;
use Text::Markdown;
use URI::Fetch;
use XML::Feed;

my $blog = param('blog') || '';

my $blog_url;
if ($blog) {
    $blog_url = "https://raw.githubusercontent.com/RobEarl/website/main/blog/${blog}/README.md";
} else {
    $blog_url = "https://raw.githubusercontent.com/RobEarl/website/main/index.md";
}

my $columns = 2;
my $start   = 0x77dddd;
my $end     = 0xffffff;

my $box_row;
for ( my $i = $end ; $i >= $start ; $i -= ( ( $end - $start ) / $columns ) ) {
    my $class = ( $i == $end ) ? 'newlinebox' : 'box';
    $box_row .=
      sprintf
      qq(<span style="background-color: #%x;" class="$class"  >&nbsp;</span>),
      $i;
}

##################
# Configuration:
#
##################
my $stackoverflow_id = 1691146;
my $stackoverflow_url = "http://stackoverflow.com/feeds/user/$stackoverflow_id";
my $template = <<"TEMPLATE";
Content-type: text/html

<html>
<head>
<title>Robert Earl's Website</title>
<link rel="stylesheet" type="text/css" href="/main.css" />
<meta name="google-site-verification" content="S6rv_lSoYeoWtTinzTXAgeDz0Tq9dlNHwH778Js3Qxs" />
</head>
<body>
<div id="header">
<span id="title">Robert Earl</span>
<div id="boxes">
$box_row
$box_row
$box_row
$box_row
$box_row
</div>
</div> 
    
<div id="content">
<table id="stackoverflow">
<tr><th colspan=2>
<a href="http://stackoverflow.com/users/1691146/robearl">
<img src="http://stackoverflow.com/users/flair/1691146.png" width="208" height="58" alt="profile for RobEarl at Stack Overflow, Q&amp;A for professional and enthusiast programmers" title="profile for RobEarl at Stack Overflow, Q&amp;A for professional and enthusiast programmers">
</a>
</th></tr>
[% count = 0 %]
[% FOREACH item = stackoverflow.items %]
[% count = count + 1 %]
[% LAST IF count > 5 %]
[% IF (matches = item.title.match('^Comment')) %]
[% ELSIF (matches = item.title.match('^Answer')) %]
<tr><th class="answer">A</th><td><a href="[% item.link.replace('(.*?)/questions/([0-9]+)/.*', '\$1/q/\$2/$stackoverflow_id') %]">[% item.title.replace('^Answer by.*?for ', '') %]</a><td></tr>
[% ELSE %]
<tr><th class="question">Q</th><td><a href="[% item.link.replace('(.*?)/questions/([0-9]+)/.*', '\$1/q/\$2/$stackoverflow_id') %]">[% item.title %]</a><td></tr>
[% END %]

[% END %]
</table>

<div class="post">
[% blog %]
</div>

</div>

<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-38573731-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>

</body>
TEMPLATE


##################
##################

my $tt = Template->new( #DEBUG => DEBUG_ALL,
			'STRICT' => 1
	)
  or die "Failed to load template: $Template::ERROR\n";

my $blog;
my $res = URI::Fetch->fetch($blog_url);
if ($res && $res->is_success) {
    my $m = Text::Markdown->new;
    $blog = $m->markdown($res->content);
}

my $stackoverflow = XML::Feed->parse(URI->new($stackoverflow_url));# or die XML::Feed->errstr;

$tt->process( \$template, { 'blog' => ($blog || "Not Found"),
                            'stackoverflow' => ($stackoverflow || {'items'=>[]}) })
  or die $tt->error();

