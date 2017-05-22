//列挙
function myutil(m){
	$(m).find('[activelist]').submit(function(){
		//最初だけ
		this.mihon=this.mihon||$(this).children(":last").prop('outerHTML')
		this.canjson=this.mihon?true:false
        $(this).children().remove()
        $(this).change()
	}).change(function(){
		function update(list,posbgn,posend){
			list.canjson=false
			console.log("update")
			$.ajax({
				url:$(list).attr("activelist"),
				type:'post',
				dataType:'json',
				data:{
					"posbgn":posbgn,
					"posend":posend
				},
				list:list,
				success:function(data){
				    console.log(data)
					data=data["list"]
					if(data&&data.length){
						var getvar=function(v,tmp){
							v=v["data"]
							if(tmp){
								for(var j of tmp.split(".")){v=v[j]}
							}
							return (typeof v === "undefined")?"":v
						}
						for(var i of data){
							var val,text=this.list.mihon
							text=text.replace(/\[\[([\w\-./]*)(\|minsec)?(\|bool:([\w\-./]*):([\w\-./]*))?(\|def:([\w\-./]+))?\]\]/g,function(tmp,g1,g2,g3,g4,g5,g6,g7){
								val=getvar(i,g1)
								if(g2){val=parseInt(val);val=Math.floor(val/60)+":"+val%60;}
								if(g3){val=val?g4:g5}
								if(g6){val=val||g7}
								return val
							})
							var elem=$(text)
							$(this.list).append(elem)
							elem.attr("pos",i["pos"])
							myutil(elem)
						}
						this.list.canjson=true
					}else{
						this.list.canjson=false
					}
				}
			})
		}
		if(this.canjson){
			if(0){
			}else if($(this).find("[pos]").length==0){
			    console.log("a")
				update(this,null,null)
			}else if(($(window).scrollTop()+$(window).height())>$(this).offset().bottom){
			    console.log("b")
				update(this,$(this).children("[pos]:last").attr("pos"),null)
			}
		}
	}).submit()
	//再生位置指定
	$(m).find("[currenttime]").on("loadeddata",function(){
		this.currentTime=parseFloat($(this).attr("currenttime"))
	})
	//即表示
	$(m).find("input[src]").change(function(){
		m=$('#'+$(this).attr("src"))
		m.attr("src",URL.createObjectURL(this.files[0]))
		m.attr("disabled",false)
	})
	//要素画像時刻
	$(m).find("form").submit(function(){
		$(this).find("[tmp]").remove()
		$(this).find("input[snap]").each(function(i,m){
			var n=$("#"+$(m).attr("snap"))
			var name=$(m).attr("name")
			var snapw=parseInt($(m).attr("snapw"))
			var snaph=parseInt($(m).attr("snaph"))
			if(!n.attr("disabled")){
				$(m).after("<canvas hidden tmp name="+name+" width="+snapw+" height="+snaph+" />")
				var c=$("canvas[name="+name+"]")[0]
				c.getContext("2d").drawImage(n[0],0,0,snapw,snaph);
				$(m).attr("value",c.toDataURL("image/jpeg"))
			}
		})
		$(this).find("input[play]").each(function(i,m){
			var n=$("#"+$(m).attr("play"))
			var name=$(m).attr("name")
			$(m).after("<input hidden tmp name="+name+"pos value="+n[0].currentTime+" /><input hidden tmp name="+name+"len value="+n[0].duration+" />")
		})
		if($(this).is("[same][alert]")){
			var same=$(this).attr("same")
			var val=0
			$(this).find("."+same).each(function(i,m){
				if(val==0){
					val=$(m).val()
				}else{
					if(val!=$(m).val()){
						val=1
						return false;
					}
				}
			})
			if(val==1){
				alert($(this).attr("alert"))
				return false;
			}
		}
		if($(this).is("[ajaxsubmit]")){
			$.ajax({
				url:$(this).attr("action")||"/",
				type:"post",
				data:new FormData(this),
				contentType:false,
				processData:false,
				this:this,
				xhr:function(){
					XHR=$.ajaxSettings.xhr()
					if(XHR.upload){
						XHR.upload.this=this.this
						XHR.upload.addEventListener('progress',function(e){
							percent=e.loaded/e.total*100
							$(this.this).find(".ajaxbar").css("width",percent+"%")
							$(this.this).find(".ajaxtxt").text(percent+"%")
						},false)
					}
					return XHR
				},
				complete:function(xhr){
					$(this.this).find(".ajaxtxt").text((xhr.status==200)?("complete"):(xhr.status+">"+xhr.statusText+">"+xhr.responseText))
					$(this.this).find(".ajaxbar").css("width","0%")
					var attr=$(this.this).attr("ajaxsubmit")
					$('.'+attr).submit()
					setTimeout(function(){$('.'+attr+'late').submit()},400)
				}
			})
			return false
		}
	})
}
$(window).scroll(function(){
	$("[activelist]").change()
});
myutil(document)