(function(){
  function boot(){
    var btn=document.querySelector('.air-embed .ai-generator .btn');
    var ta=document.querySelector('.air-embed .ai-input');
    if(!btn||!ta||btn.dataset.wired) return;
    btn.dataset.wired='1';
    var out=document.createElement('div');
    out.className='air-lyrics';
    out.style.cssText='margin-top:14px;padding:14px 16px;border-radius:12px;background:rgba(0,0,0,.38);border:1px solid rgba(0,212,255,.35);color:#dff6ff;font-size:.9rem;white-space:pre-line;text-align:left;display:none';
    btn.parentNode.appendChild(out);
    btn.addEventListener('click', function(){
      var prompt=ta.value.trim()||'a neon-lit love song for the metaverse';
      var PROF=(window.AIMV_PROFILE&&window.AIMV_PROFILE.get())||{};
      var pe=PROF.persona||{};
      var hooks={love:'your avatar and mine, tangled in the cloud',neon:'neon lights over the grid tonight',rise:'we boot up, we rise, we render the sky',run:'chasing photons down the databed'};
      var key=(prompt.toLowerCase().match(/love|neon|rise|run/)||['neon'])[0];
      var hook=hooks[key];
      var sign=pe.sign||'Aquarius', top=pe.top||'Curiosity';
      var lyrics='[Verse 1]\n'+prompt.split(/\s+/).slice(0,6).join(' ')+' — I heard it in the static,\n'+hook+',\n'+sign+' child with a '+top.toLowerCase()+' habit,\nwriting our names in the cache.\n\n[Chorus]\n'+hook+'\n'+hook+'\n(say it in my cloned voice, say it twice)\n\n[Verse 2]\nMixer down, AI FX at ninety,\nevery ghost in the studio is friendly,\ncopyright-free and heartbeat-ready —\npress generate and mean it.';
      out.style.display='block';
      out.textContent='🎼 “'+prompt+'”\n\n'+lyrics;
      out.scrollIntoView({behavior:'smooth',block:'nearest'});
      if(window.AIMV_HUMANOID) window.AIMV_HUMANOID.speak('Lyrics drafted from your prompt. '+lyrics.replace(/\n+/g,'. ').slice(0,200));
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot); else boot();
})();
