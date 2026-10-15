/**
 * Seguimiento WebAR Ferrisariato siguiendo San Sebastián (Gaussian-AR):
 * Android con WebXR immersive-ar / ARCore -> nativo;
 * Android sin WebXR -> 8th Wall; iPhone -> 8th Wall;
 * escritorio -> visor 3D, sin motor AR.
 */
export function preferredTracking({mobile,ios,nativeSupported,xr8Available,override=''}) {
 if(!mobile)return 'none';
 if(override==='xr8'&&xr8Available)return 'xr8';
 if(ios)return xr8Available?'xr8':'none';
 if(nativeSupported)return 'native';
 return xr8Available?'xr8':'none';
}
