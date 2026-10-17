export class PinballAudio {
  constructor(){this.enabled=true;this.context=null;this.played=0;}
  async unlock(){
    // Create/resume synchronously from a tap or key press when possible.
    // Safari may report "interrupted" instead of "suspended" after a prompt.
    if(!this.context){
      const C=window.AudioContext||window.webkitAudioContext;
      if(!C)return false;
      this.context=new C();
    }
    if(this.context.state!=='running'){
      try{await this.context.resume();}
      catch(error){console.warn('Could not resume pinball audio',error);return false;}
    }
    return this.context.state==='running';
  }
  // Seven-note ascending chime, with a bright chord on the seventh target.
  bonusStep(index){
    if(!this.enabled||!this.context||this.context.state!=='running')return;
    const c=this.context,t=c.currentTime;
    const melody=[523.25,587.33,659.25,698.46,783.99,880,1046.5];
    const notes=index===6?[1046.5,1318.5,1568]:[melody[index]];
    for(const [i,hz] of notes.entries()){
      const osc=c.createOscillator(),gain=c.createGain(),start=t+i*.018;
      osc.type='sine';osc.frequency.setValueAtTime(hz,start);
      osc.frequency.exponentialRampToValueAtTime(hz*.99,start+.2);
      gain.gain.setValueAtTime(.0001,start);
      gain.gain.exponentialRampToValueAtTime(index===6?.11:.095,start+.009);
      gain.gain.exponentialRampToValueAtTime(.0001,start+(index===6?.48:.22));
      osc.connect(gain);gain.connect(c.destination);osc.start(start);
      osc.stop(start+(index===6?.5:.24));
      osc.onended=()=>{osc.disconnect();gain.disconnect();};
      this.played++;
    }
  }
  play(kind,id=''){
    if(!this.enabled)return;
    if(!this.context||this.context.state!=='running'){
      // Avoid losing the first cue when AudioContext.resume() is asynchronous.
      void this.unlock().then(ready=>{if(ready&&this.enabled)this.play(kind,id);});
      return;
    }
    const c=this.context,t=c.currentTime;const osc=c.createOscillator(),gain=c.createGain();
    const variation=[...id].reduce((s,v)=>s+v.charCodeAt(0),0)%7;
    const freq=kind==='target'?700+variation*75:kind==='bumper'?390+variation*55:kind==='sling'?240:kind==='launch'?120:kind==='finish'?200:90;
    osc.type=kind==='target'?'sine':'triangle';osc.frequency.setValueAtTime(freq,t);osc.frequency.exponentialRampToValueAtTime(freq*.45,t+.14);
    gain.gain.setValueAtTime(.0001,t);gain.gain.exponentialRampToValueAtTime(.13,t+.006);gain.gain.exponentialRampToValueAtTime(.0001,t+.19);
    osc.connect(gain);gain.connect(c.destination);osc.start(t);osc.stop(t+.2);osc.onended=()=>{osc.disconnect();gain.disconnect();};this.played++;
  }
}
