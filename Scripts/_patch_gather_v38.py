from pathlib import Path
hud = Path(r'D:\DEVELOPMENT\Games\IsekaiVillage\Source\IsekaiVillage\IsekaiVillageHUD.cpp')
t = hud.read_text(encoding='utf-8')
if 'GatherInventoryComponent.h' not in t:
    t = t.replace('#include "IsekaiVillageCharacter.h"', '#include "IsekaiVillageCharacter.h"\n#include "GatherInventoryComponent.h"')
    hud.write_text(t, encoding='utf-8')
    print('hud include ok')
else:
    print('hud already')
portal = Path(r'D:\DEVELOPMENT\Games\IsekaiVillage\Source\IsekaiVillage\IslandWarpPortal.cpp')
t = portal.read_text(encoding='utf-8')
old = '\tif (!bHasWarped && bPlayerInside && ChargeTime >= MaxChargeTime && !DestinationLevel.IsNone())\n\t{\n\t\tbHasWarped = true;'
new = '''\tif (!bHasWarped && bPlayerInside && ChargeTime >= MaxChargeTime && !DestinationLevel.IsNone())
\t{
\t\tif (RequiredLevel > 0)
\t\t{
\t\t\tAPlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr;
\t\t\tAIsekaiVillageCharacter* Character = PC ? Cast<AIsekaiVillageCharacter>(PC->GetPawn()) : nullptr;
\t\t\tif (Character && Character->GetGatherLevel() < RequiredLevel)
\t\t\t{
\t\t\t\tChargeTime = 0.0f;
\t\t\t\tif (GEngine)
\t\t\t\t{
\t\t\t\t\tGEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, FString::Printf(TEXT("Need gather level %d"), RequiredLevel));
\t\t\t\t}
\t\t\t\treturn;
\t\t\t}
\t\t}
\t\tbHasWarped = true;'''
if old in t:
    t = t.replace(old, new)
    if '#include "Engine/Engine.h"' not in t:
        t = t.replace('#include "Kismet/GameplayStatics.h"', '#include "Engine/Engine.h"\n#include "Kismet/GameplayStatics.h"')
    portal.write_text(t, encoding='utf-8')
    print('portal ok')
else:
    print('portal pattern missing')
