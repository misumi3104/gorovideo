function myplayer(play,user){
	play=$(play[0])
	video=play.find("video")[0]
	video.user=user
	//初期設定
	if($(video).attr("src")){
		$(video).append('<source src="'+$(video).attr("src")+'"></source>').removeAttr("src")
	}
	play.find("video source").each(function(i,m){
		$(m).parents(".play").find(".source").append('<div class="drop drop-hidden" src="'+$(m).attr("src")+'" style="bottom:'+100*(i+1)+'%;"><p>'+$(m).attr("name")+'</p></div>')
	})
	//動作
	function update(play,video){
		if(video.paused){
			play.addClass("play-paused")
		}else{
			play.removeClass("play-paused")
		}
		if(video.user.update){
			video.user.update(play,video)
		}
	}
	function interval(play,video){
		minsec=function(sec){
			if(isNaN(sec))return "-:--";
			sec=Math.floor(sec)
			min=Math.floor(sec/60)
			sec=sec-min*60
			return min+":"+('00'+sec).slice(-2)
		}
		play.find(".time>p").text(minsec(video.currentTime)+"/"+minsec(video.duration))
		play.find(".progresspos").css("width",(video.duration?video.currentTime/video.duration*100:0)+"%");
		if((--video.timer<0)&&(!video.paused)){
			play.addClass("play-hidden")
		}
		if(video.user.interval){
			video.user.interval(play,video)
		}
	}
	setInterval(interval,1000,play,video)
	play.mousemove(function(){
		video.timer=2
		if(play.hasClass("play-hidden")){
			play.removeClass("play-hidden")
		}
	})
	play.find("[src]").click(function(){
		play=$(this).parents(".play")
		video=play.find("video")[0]
		video.src=$(this).attr("src")
	})
	play.find(".button").click(function(){
		play=$(this).parents(".play")
		video=play.find("video")[0]
		if(video.paused){
			video.play()
		}else{
			video.pause()
		}
		update(play,video)
	})
	play.find(".progressbar").on("click mousemove",function(e){
		if(e.which){
			play=$(this).parents(".play")
			video=play.find("video")[0]
			video.currentTime=e.offsetX/$(this).width()*video.duration
			interval(play,video)
			update(play,video)
		}
	})
	play.find(".source").click(function(e){
		if($(this).find(".drop-hidden").length){
			$(this).find(".drop").removeClass("drop-hidden")
		}else{
			$(this).find(".drop").addClass("drop-hidden")
		}
	})
	play.find(".full").click(function(){
		function callfuncs(element,list){
			for(var func of list){if(element[func]){element[func]();return true;}}
			return false;
		}
		play=$(this).parents(".play")
		if(document.fullscreenElement||document.webkitFullscreenElement||document.mozFullScreenElement||document.msFullscreenElement||null){
			if(callfuncs(document,["exitFullscreen","webkitExitFullscreen","mozCancelFullScreen","msExitFullscreen"])){
				play.removeClass("play-full");
			}
		}else{
			if(callfuncs(play[0],["requestFullscreen","webkitRequestFullScreen","mozRequestFullScreen","msRequestFullscreen"])){
				play.addClass("play-full")
			}
		}
	})
	//状況反映
	function playinit(){
		update(play,video)
		interval(play,video)
		play.find("video source").each(function(i,m){
			if(video.currentSrc.indexOf($(m).attr("src"))>=0){play.find(".source>p").text($(m).attr("name"))}
		})
	}
	playinit()
	$(video).on("loadstart",playinit)
}