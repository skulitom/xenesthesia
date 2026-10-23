// Original Xenesthesia code, MIT. Only coordinates of our colour detail layer.
bool XenWorldColour(float4 baseRow, float4 detailRow)
{
    float scale = dot(detailRow.xy, baseRow.xy) / max(dot(baseRow.xy, baseRow.xy), 0.000001);
    return abs(scale + 1337.0) < 0.1;
}

float2 XenWorldColourUV(float3 worldPos)
{
    // A continuous oblique projection: same point -> same colour, independent
    // of the camera and each surface's material, texture origin or scale.
    return float2(dot(worldPos, float3(0.0031, 0.0019, 0.0024)),
                  dot(worldPos, float3(-0.0017, 0.0034, 0.0011)));
}
