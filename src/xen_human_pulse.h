// Original Xenesthesia deformation (MIT). Applied after native flex/skinning.
// A shared entity-relative field also handles CPU-skinned facial fragments.
void XenHumanPulse(inout float3 position, float amount)
{
    float head = smoothstep(48.0, 60.0, position.z);
    float3 fromHead = position - float3(0.0, 0.0, 64.0);
    position += fromHead * float3(1.0, 1.0, 0.45) * (head * amount);
    float torso = saturate(position.z / 36.0) * (1.0 - head);
    position.xy *= 1.0 + torso * amount * 0.18;
}

void XenHumanPulseWorld(inout float3 worldPos, float3 entityOrigin, float amount)
{
    float3 localPos = worldPos - entityOrigin;
    XenHumanPulse(localPos, amount);
    worldPos = entityOrigin + localPos;
}

void XenNpcPulseWorld(inout float3 worldPos, float3 worldNormal,
                     float3 entityOrigin, float marker)
{
    if (marker < 1001.0)
        XenHumanPulseWorld(worldPos, entityOrigin, marker - 1000.0);
    else
        worldPos += worldNormal * ((marker - 1001.0) * 8.0);
}
