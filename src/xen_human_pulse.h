// Original Xenesthesia deformation (MIT). Applied after flex, before skinning.
// A shared position field keeps skin, hair, teeth and eyes together.
void XenHumanPulse(inout float3 position, float amount)
{
    float head = smoothstep(48.0, 60.0, position.z);
    float3 fromHead = position - float3(0.0, 0.0, 64.0);
    position += fromHead * float3(1.0, 1.0, 0.45) * (head * amount);
    float torso = saturate(position.z / 36.0) * (1.0 - head);
    position.xy *= 1.0 + torso * amount * 0.18;
}
