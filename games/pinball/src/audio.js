export class PinballAudio {
  constructor(){this.enabled=true;this.context=null;this.played=0;}
  async unlock(){if(!this.context){const C=window.AudioContext||window.webkitAudioContext;if(C)this.context=new C();}if(this.context?.state==='suspended')await this.context.resume();}
  play(kind,id=''){
    if(!this.enabled||!this.context||this.context.state!=='running')return;
    const c=this.context,t=c.currentTime;const osc=c.createOscillator(),gain=c.createGain();
    const variation=[...id].reduce((s,v)=>s+v.charCodeAt(0),0)%7;
    const freq=kind==='target'?700+variation*75:kind==='bumper'?390+variation*55:kind==='sling'?240:kind==='launch'?120:kind==='finish'?200:90;
    osc.type=kind==='target'?'sine':'triangle';osc.frequency.setValueAtTime(freq,t);osc.frequency.exponentialRampToValueAtTime(freq*.45,t+.14);
    gain.gain.setValueAtTime(.0001,t);gain.gain.exponentialRampToValueAtTime(.13,t+.006);gain.gain.exponentialRampToValueAtTime(.0001,t+.19);
    osc.connect(gain);gain.connect(c.destination);osc.start(t);osc.stop(t+.2);osc.onended=()=>{osc.disconnect();gain.disconnect();};this.played++;
  }
}
