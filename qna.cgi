#!/usr/bin/perl
$header	 = "./qna.html";
$skin_body	 = "./body.html";
$skin_edit	 = "./edit.html";
$skin_search = "./search.html";
$qna_log = "./qna.log";
$password = "1111";
$nitems = 3;
$page_size = 100;
@key = ('num', 'q', 'a', '' );

&get_form;
&get_cookie; 

$ip = $ENV{'REMOTE_ADDR'};
$search = $query{'search'};

if ( $query{'m'} eq 'reg' && $query{'q'} eq '' ) {
	print qq|Content-type:text/html\n\n|;
	print qq|<script language="javascript">alert("질문을 입력하셔야죠~~");history.go(-1);</script>|;
	exit;
}

# 관리자 로그인 처리
$admin = 1 if ($COOKIE{'ren'} eq $password && $query{'m'} ne 'logout');

if ($query{'m'} eq 'login') { 
	if ($query{'pwd'} ne $password) {		
		$dmi = qq|<p><form method=post action="qna.cgi"><input type=hidden name="m" value="login"><table border=1 cellspacing=0 cellpadding=0 bgcolor="#ffeeee" style="filter:alpha(opacity=70)"><tr><td><table width=100% cellspacing=0 cellpadding=2 border=0>|;
		$dmi .= qq|<tr><td colspan=3 align=center><font size=2 color="black">로그인을 위해 패스워드를 입력해주세요. <a href="qna.cgi?m=logout"><font color=red>(LOGOUT)</font></a></font></td></tr>|;
		$dmi .= qq|<tr><td align=center><font size=2 color="black">ADMIN PASSWORD</font></td><td align=center><input type=password name=pwd size=10></td><td align=center><input type=submit value="carrot!"></td></tr></table></td></tr></table></form>|;
		
	}
	else { 
		print "Set-Cookie: ren=$query{'pwd'}\n";
		$admin = 1; 
	}
} 
elsif ($query{'m'} eq 'logout') {
	print "Set-Cookie: ren=\n"; 
	$admin = 0; 
}

# HTML 스킨 파일 읽어오기
open(IN,"$header") || &error("Can't open $header",'NOLOCK');
@lines = <IN>;
close(IN);

open(IN,"$skin_body") || &error("Can't open $skin_body",'NOLOCK');
@lines_body = <IN>;
close(IN);

open(IN,"$skin_edit") || &error("Can't open $skin_edit",'NOLOCK');
@lines_edit = <IN>;
close(IN);

if (open(IN,"$skin_search"))
{
	@lines_search = <IN>;
	close(IN);
}

print qq|Content-type:text/html\n\n|;
foreach $line (@lines) {
	$line =~ s/<!--\@dmi-->/$dmi/i;
	print $line;
}

if ($admin == 1) {
	print qq|<a href="qna.cgi?m=logout">Logout</a> |;	
}
else {
	print qq|<a href="qna.cgi?m=login">Admin</a> |;
}

print qq|</font></form><hr>|;

if ( substr($ip, 0, 7) == "141.223" || substr($ip, 0, 7) == "143.248" )
{
	
}

### 질문 입력 처리
if ($query{'m'} eq 'reg' ) {
	$q = $query{'q'};
	$q =~ s/\|//eg;
	@TOTLOG = &get_file($qna_log);
	$num = $TOTLOG[0] + 0;
	$num += 1;
	shift(@TOTLOG);
	
	# 2002.5.13
	$ttt = get_vtime(time);
	# 2002.9.29
	$msg = $num."|".$q."||$ttt|$ip|\n";
	
	push(@NEWLOG, $msg);
	
	foreach $LOG (@TOTLOG) {
		push(@NEWLOG, $LOG);
	}
	&put_file($qna_log, ("$num\n", @NEWLOG));
	undef(@NEWLOG);
}

### 답변 처리
if ($admin == 1 && $query{'num'} ne '')
{
	$re_num = $query{'num'};
	@TOTLOG = &get_file($qna_log);
	$num = $TOTLOG[0] + 0;
	shift(@TOTLOG);
	foreach $row (@TOTLOG) {
		@TMP = split(/\|/, $row);
		if ($TMP[0] eq $re_num) {
			$msg = '';
			foreach (0 .. 1) {
				$msg .= $TMP[$_]."|";	
			}
			# 2002.5.13 날짜 추가
			
			#답변 추가
			if ($TMP[3] ne '' && $TMP[3] != NULL) {
				$msg .= $query{'a'}."|$TMP[3]|\n";
			}
			else {
				$msg .= $query{'a'}."|\n";
			}
		}
		else {
			$msg = $row;
		}
		push(@NEWLOG, $msg);
	}
	&put_file($qna_log, ("$num\n", @NEWLOG));
	undef(@NEWLOG);
}

# 삭제 처리
if ($admin == 1 && $query{'del'} ne '')
{
	$del_num = $query{'del'};
	@TOTLOG = &get_file($qna_log);
	$num = $TOTLOG[0] + 0;
	shift(@TOTLOG);
	foreach $row (@TOTLOG) {
		@TMP = split(/\|/, $row);
		if ($TMP[0] ne $del_num) {
			push(@NEWLOG, $row);
		}
	}
	&put_file($qna_log, ("$num\n", @NEWLOG));
	undef(@NEWLOG);	
}

# 질문 리스트 보여주기
@TOTLOG = &get_file($qna_log);
$page = $query{'page'};
shift(@TOTLOG);
$count = 0;
if ($page == "") {
	$page = 1;
}

foreach $row (@TOTLOG) {
	if ($count >= ($page-1)*$page_size && $count < ($page)*$page_size) {

		# 검색 처리
		if ( $search )
		{ 
			if (! ( $row =~ /($search)/ ))
			{
				next;
			}
			# 있으면 하일라이트
			$highlight = "<font color=red>$search</font>";
			$row =~ s/$search/$highlight/g;
		}
		@TMP = split(/\|/, $row);

		if ($TMP[2] eq '') {
			# 답변이 없으면 회색으로
			$color = "#AAAAAA";
		}
		else {
			$color = "#000000";
		}
		
		$number = $TMP[0];
		$question = $TMP[1];
		
		# 2002.5.13 날짜 출력기능 추가
		if ($TMP[3] ne "" && $TMP[3] != NULL) {
			$year = substr($TMP[3],0,4);
			$mon = substr($TMP[3],4,2);
			$day = substr($TMP[3],6,2);
			$hour = substr($TMP[3],8,2);
			$min = substr($TMP[3],10,2);
			$ttt = "$year/$mon/$day $hour:$min";
			$mytime = $ttt;
		}
			
		$answer = $TMP[2];
	
		# 스킨을 입힌 결과를 출력
		foreach $line (@lines_body) {
			$temp_line = $line;
			$temp_line =~ s/\@color/$color/g;
			$temp_line =~ s/\@number/$number/g;
			$temp_line =~ s/\@question/$question/g;
			$temp_line =~ s/\@answer/$answer/g;
			$temp_line =~ s/\@time/$mytime/g;
			$temp_line =~ s/\@edit/$edit/g;
			print $temp_line;
		}
		# admin 로그인인 경우 답변 할 수 있게 함.
		if ($admin == 1){
			print qq|<input type=button value="삭제" OnClick="location.href='qna.cgi?del=$TMP[0]'">|;
			if ($TMP[2] eq '') {
				print qq| <form	method=post action="qna.cgi"><input type=hidden name="num" value="$TMP[0]"><input type=text name="a" size=60><input type=submit value="답변"></form>|;
			}
		}
		

		if ($admin == 1 && $TMP[2] ne '')
		{
		# 답변 편집기능 추가 
			foreach $line (@lines_edit) {
				$temp_line = $line;
				$temp_line =~ s/\@number/$number/g;
				$temp_line =~ s/\@answer/$answer/gi;
				print $temp_line;
			}

		}
		else
		{
			print "<br><br>\n";
		}


	}
	$count++;
}

# 검색폼 출력
foreach $line (@lines_search) {
	print $line;
}


# 페이지 처리
print qq|<font size=2>|;
$i = 1;
while($i < ($count / $page_size)+1) {
	if ($i != $page) {
		print qq|<a href="qna.cgi?page=$i">[$i]</a>&nbsp;|;
	}
	else {
		print qq|[$i]&nbsp;|;
	}
	$i++;
}

exit;

sub parse_log { chomp(@TMP); foreach (0 .. $nitems) { $F{$sister_princess[$_]} = $TMP[$_]; } }

sub get_form {
    if ($ENV{'QUERY_STRING'}) { &PUrlEncode($ENV{'QUERY_STRING'}); }
    else {
        binmode STDIN;
        read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
        &PUrlEncode($buffer);
    }
}

sub get_cookie {
    @COOKIES = split(/; /,$ENV{'HTTP_COOKIE'});
    foreach (@COOKIES) {
        ($ck_name,$ck_value) = split(/=/,$_);
		$ck_value =~ tr/+/ /;
		$ck_value =~ s/%([a-fA-F0-9]{2})/pack("c",hex($1))/eg;
		$COOKIE{$ck_name} = $ck_value;
    }
	$cookie{'cname'} = $cookie{'cemail'} = $cookie{'curl'} = '';
    @pairs = split(/,/,$COOKIE{$cookie_id});
	foreach $pair (@pairs) {
        ($key, $value) = split(/\|/, $pair);
        $cookie{$key} = $value;
    }
	$cookie{'curl'} = 'http://' if ($cookie{'curl'} eq '');
	$cook = 'checked' if ($cookie{'cname'} eq '');
}

sub PUrlEncode {
	@pairs = split(/&/, $_[0]);
    foreach $pair (@pairs) {
        ($key, $value) = split(/=/, $pair);
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$query{$key} = $value; $miko{$value} = 'koishiteiruno' if ($key eq 'mizuho');
    }
}

sub get_file {
	open(FILEGET, "$_[0]"); @FILEGET = <FILEGET>; 
	close(FILEGET);
	@FILEGET;
}

sub put_file {
	($filename, @putdata) = @_;
	open(FILEPUT, ">$_[0]"); print FILEPUT @putdata;
	close(FILEPUT);
}

sub lock {
	my($retry) = 10; my($flag) = 0;
	if ($lock == 1) { 
		while (!symlink(".", $lockfile)) {
			if (--$retry <=0 ) { unlink($lockfile) if (-e $lockfile); &msg_error("File Lock", "$!"); }
			sleep(1);
		}
	} elsif ($lock == 2) {
		foreach (1 .. $retry) {
			if (-e "$lockfile") { sleep(1); }
			else { open(LOCK, ">$lockfile"); close(LOCK) || &msg_error("File Lock", "$!"); $flag = 1; last; }
		}
		&msg_error("File Lock", "$!") if ($flag == 0);
	}
}

sub unlock { unlink($lockfile) if (-e $lockfile); }

sub get_vtime {
	my(@tmp); my($vt);
	if (length $_[0] != 15) {	
		@tmp = localtime($_[0]);
		foreach (0 .. 5) { 
			if ($_ == 4) { $tmp[4] += 1; }
			elsif ($_ == 5) {
				$tmp[5] += 1900 if (length $tmp[5] < 4);
				$tmp[5] += 100 if ($tmp[5] <= 1970);
			}
			$tmp[$_] = "0$tmp[$_]" if ($tmp[$_] < 10);
			$vt = $tmp[$_]. $vt; 
		}
		$vt .= $tmp[6];
	} 
	else { $vt = $_[0]; }
	$vt;
}
